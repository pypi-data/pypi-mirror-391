from collections import defaultdict
from dataclasses import dataclass
import enum
import json
import logging
import os
from pathlib import Path
import sys
from typing import Dict, List, Set, Any, Union

import ijson
import yaml


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class EC2Instance:
    """
    Represents an EC2 instance.
    """
    file_address: tuple[int, int]  # The reservation position in the Reservations list, and instance position in the Instances list.
    instance_id: str
    tags: Dict[str, str]
    enis: 'list[ENI]'
    vpc_id: str


@dataclass(slots=True)
class ENI:
    """
    Represents an ENI instance.
    """
    file_address: tuple[int]  # The position in the NetworkInterfaces list
    eni_id: str
    subnet_id: str
    security_group_ids: list[str]
    ec2_attached_id: str
    attachment_type: str
    tags: Dict[str, str]

    def group_key(self, instance_tag_parts: list[str], use_sg: bool) -> str:
        group_key_parts = [self.subnet_id]
        if use_sg:
            group_key_parts.extend(sorted(self.security_group_ids))
        group_key_parts.extend(instance_tag_parts)
        return ":".join(group_key_parts)


class PruneLevel(enum.Enum):
    LEVEL_0_REMOVE_ALL_EC2 = 0
    LEVEL_1_ONE_EC2_PER_SUBNET = 1
    LEVEL_2_ONE_EC2_PER_SUBNET_AND_SECURITY_GROUP = 2


@dataclass
class UserConfig:
    prune_level: PruneLevel
    filter_exclude: List[Dict[str, str]] | None = None
    filter_include: List[Dict[str, str]] | None = None
    group_by: List[str] | None = None
    enabled: bool = True

    @classmethod
    def from_file(cls, path: os.PathLike) -> "UserConfig":
        with open(path, "r") as f:
            return cls.from_yaml(f)
    
    @classmethod
    def from_yaml(cls, f) -> "UserConfig":
        config = yaml.safe_load(f)
        if config is None or not isinstance(config, dict) or "aws_pruner" not in config or not isinstance(config["aws_pruner"], dict):
            return cls.from_dict({})
        return cls.from_dict(config["aws_pruner"])

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "UserConfig":
        allowed_keys = {"prune_level", "filter_exclude", "filter_include", "group_by", "enabled"}
        unexpected_keys = set(config.keys()) - allowed_keys
        if unexpected_keys:
            raise ValueError(f"Unexpected keys: {unexpected_keys}. Permitted keys: {sorted(allowed_keys)}.")
        try:
            config["prune_level"] = PruneLevel[config.get("prune_level", "LEVEL_1_ONE_EC2_PER_SUBNET")]
        except KeyError as e:
            valid_levels = [level.name for level in PruneLevel]
            raise ValueError(f"Unrecognized prune_level '{e.args[0]}'. Valid options: {valid_levels}")
        return cls(**config)


class AwsPruneTool:
    """
    Prunes AWS configurations by eliminating redundant ENIs (Elastic Network
    Interfaces) and associated EC2 nodes.  It maintains the invariant that for every
    combination of subnet and security group that initially has at least one ENI, at least
    one ENI remains after pruning.

    Args:
        dir_aws_config: Path to the directory containing Reservations.json, NetworkInterfaces.json, etc.
        filter_exclude: Always remove ENIs if attached to an EC2 node matching ALL tags in ANY of the list items.
        filter_include: Always remove ENIs if attached to an EC2 node NOT matching ALL tags in ANY of the list items.
        group_by: Maintain one ENI per subnet and security group per unique label value.
    """

    def __init__(
        self,
        aws_config_dir: os.PathLike,
        prune_level: PruneLevel,
        filter_exclude: List[Dict[str, str]] | None,
        filter_include: List[Dict[str, str]] | None,
        group_by: List[str] | None,
    ):
        self.dir_aws_config = Path(aws_config_dir)
        self.prune_level = prune_level
        self.filter_exclude = filter_exclude
        self.filter_include = filter_include
        self.group_by = group_by

        self.instances: dict[str, EC2Instance] = {}
        self.enis: dict[str, ENI] = {}
        self.network_interfaces: Dict[str, Any] = {}
        self.security_groups : Dict[str, Any] = {}
        # Each item is a list of file addresses to remove; during removal we will merge the lists
        self.enis_to_remove: list[list[int]] = []
        self.instances_to_remove: list[list[tuple[int, int]]] = []

    def load(self):
        """Load from target files."""
        self._load_data_inst()
        self._load_data_eni()

    def _load_data_inst(self) -> None:
        """Loads the necessary JSON data."""
        with open(self.dir_aws_config / "Reservations.json", "r") as f:
            items = ijson.items(f, 'Reservations.item')
            for res_i, item in enumerate(items):
                try:
                    for inst_i, instance in enumerate(item['Instances']):
                        ec2_instance = EC2Instance(
                            file_address=(res_i, inst_i),
                            instance_id=instance['InstanceId'],
                            enis=[],
                            tags={tag['Key']: tag['Value'] for tag in instance.get('Tags', [])},
                            vpc_id=instance['VpcId']
                        )
                        self.instances[ec2_instance.instance_id] = ec2_instance
                except KeyError:
                    logger.warning(f"Skipping instance {res_i} due to missing data.")
                    print(item)
                    continue

    def _load_data_eni(self) -> None:
        """Load ENIs from NetworkInterfaces.json"""
        with open(self.dir_aws_config / "NetworkInterfaces.json", "r") as f:
            items = ijson.items(f, 'NetworkInterfaces.item')
            for i, item in enumerate(items):

                subnet_id = item.get('SubnetId', None)
                if subnet_id is None:
                    continue
                attachment = item['Attachment']
                if attachment.get('InstanceId', None) is None or attachment.get('Status', '') != 'attached':
                    continue
                attachment_type = 'primary' if attachment.get('DeleteOnTermination', False) else 'secondary'
                ec2_attached_id = item['Attachment']['InstanceId']
                eni = ENI(
                    file_address=(i,),
                    eni_id=item['NetworkInterfaceId'],
                    subnet_id=subnet_id,
                    security_group_ids=[group['GroupId'] for group in item.get('Groups', [])],
                    ec2_attached_id=ec2_attached_id,
                    attachment_type=attachment_type,
                    tags={tag['Key']: tag['Value'] for tag in item.get('TagSet', [])}
                )
                self.enis[eni.eni_id] = eni
                self.instances[ec2_attached_id].enis.append(eni)

    def _apply_filters(self) -> None:
        """Applies include/exclude filters and returns a set of ENI IDs to remove."""
        enis_to_remove = []
        instances_to_remove = []

        if self.filter_exclude or self.filter_include:
            for instance in self.instances.values():
                if not instance.enis:
                    continue
                # Apply exclude filters first: Always remove ENIs if instance matches ANY complete exclude filter.
                if self.filter_exclude:
                    remove = False
                    for exclude_filter in self.filter_exclude:
                        if all(instance.tags.get(k) == v for k, v in exclude_filter.items()):
                            remove = True
                            break
                    if remove:
                        enis_to_remove.extend(peer.file_address for peer in instance.enis)
                        instances_to_remove.append(instance.file_address)
                        continue

                # Next, apply include filters: Remove ENIs if instance does NOT match ANY complete include filter.
                if self.filter_include:
                    remove = True
                    for include_filter in self.filter_include:
                        if all(instance.tags.get(k) == v for k, v in include_filter.items()):
                            remove = False  # Found a match, so do not remove
                            break
                    if remove:
                        enis_to_remove.extend(peer.file_address for peer in instance.enis)
                        instances_to_remove.append(instance.file_address)
                        continue

        enis_to_remove.sort()
        deduped = []
        for addr in enis_to_remove:
            if not deduped or deduped[-1] != addr:
                deduped.append(addr)
        enis_to_remove = deduped
        self.enis_to_remove.append(enis_to_remove)
        self.instances_to_remove.append(instances_to_remove)
        self._shorten_enis(enis_to_remove)
        self._shorten_instances(instances_to_remove)

    def _shorten_enis(self, enis_to_remove: List[int]) -> None:
        """Replace self.enis with a filtered version. Use a merge strategy to walk in linear time O(length enis_to_remove + length self.enis)"""

        #        enis_items = sorted(self.enis.items(), key=lambda item: item[1].file_address)
        # Already sorted by file_address
        enis_items = list(self.enis.items())
        new_enis = {}
        i, j = 0, 0
        while i < len(enis_items) and j < len(enis_to_remove):
            eni_addr = enis_items[i][1].file_address
            if eni_addr < enis_to_remove[j]:
                new_enis[enis_items[i][0]] = enis_items[i][1]
                i += 1
            elif eni_addr > enis_to_remove[j]:
                j += 1
            else:
                i += 1
        while i < len(enis_items):
            new_enis[enis_items[i][0]] = enis_items[i][1]
            i += 1

        self.enis = new_enis

    def _shorten_instances(self, instances_to_remove: List[tuple[int, int]]) -> None:
        """Replace self.instances with a filtered version. Use a merge strategy to walk in linear time O(length instances_to_remove + length self.instances)"""
        #        instances_items = sorted(self.instances.items(), key=lambda item: item[1].file_address)
        # Already sorted by file_address
        instances_items = list(self.instances.items())
        new_instances = {}
        i, j = 0, 0
        while i < len(instances_items) and j < len(instances_to_remove):
            inst_addr = instances_items[i][1].file_address
            if inst_addr < instances_to_remove[j]:
                new_instances[instances_items[i][0]] = instances_items[i][1]
                i += 1
            elif inst_addr > instances_to_remove[j]:
                j += 1
            else:
                i += 1
        while i < len(instances_items):
            new_instances[instances_items[i][0]] = instances_items[i][1]
            i += 1

        self.instances = new_instances

    def _prepare_groups(self) -> Dict[str, List[ENI]]:
        """Prepares groups based on subnet, security groups, and group_by tags."""
        groups: Dict[str, List[ENI]] = defaultdict(list)
        for instance in self.instances.values():
            instance_tag_parts = []
            if self.group_by:
                instance_tag_parts = [instance.tags.get(tag_key, "None") for tag_key in self.group_by]
            for eni in instance.enis:
                group_key = eni.group_key(instance_tag_parts, self.use_sg_key)
                groups[group_key].append(eni)
        return groups

    def _prune_ifaces_and_instances(self, groups: Dict[str, List[ENI]]) -> None:
        """Prunes ENIs within each group, keeping at least one per group."""
        enis_to_remove: list[int] = []
        instances_to_remove: list[tuple[int, int]] = []
        second_pass_instances: list[EC2Instance] = []

        # First pass: look for whole instances we can prune. All of the ENIs must be removable.
        instance_tag_parts = []
        for instance in sorted(self.instances.values(), key=lambda x: len(x.enis), reverse=True):
            instance_can_remove = True
            if self.group_by:
                instance_tag_parts = [instance.tags.get(tag_key, "None") for tag_key in self.group_by]
            for eni in instance.enis:
                group_key = eni.group_key(instance_tag_parts, self.use_sg_key)
                if len(groups[group_key]) == 1:
                    # ENI is the only one in its group
                    instance_can_remove = False
                    break
            
            if instance_can_remove:
                instances_to_remove.append(instance.file_address)
                enis_to_remove.extend(eni.file_address for eni in instance.enis)
                # Trim groups
                for eni in instance.enis:
                    group_key = eni.group_key(instance_tag_parts, self.use_sg_key)
                    groups[group_key].remove(eni)

            else:
                second_pass_instances.append(instance)

        # Second pass: look for removable secondary ENIs
        for instance in second_pass_instances:
            if self.group_by:
                instance_tag_parts = [instance.tags.get(tag_key, "None") for tag_key in self.group_by]
            for eni in instance.enis:
                if eni.attachment_type == "primary":
                    continue
                group_key = eni.group_key(instance_tag_parts, self.use_sg_key)
                if len(groups[group_key]) > 1:
                    enis_to_remove.append(eni.file_address)
                    groups[group_key].remove(eni)

        instances_to_remove.sort()
        enis_to_remove.sort()
        deduped = []
        for addr in enis_to_remove:
            if not deduped or deduped[-1] != addr:
                deduped.append(addr)
        enis_to_remove = deduped
        self.enis_to_remove.append(enis_to_remove)
        self.instances_to_remove.append(instances_to_remove)
        # Don't bother shortening the lists; we're done with them

    @property
    def use_sg_key(self):
        return self.prune_level == PruneLevel.LEVEL_2_ONE_EC2_PER_SUBNET_AND_SECURITY_GROUP

    def execute(self):
        """Execute the pruning routine. Start by applying any user-defined filters. Then preprare the grouping and prune level information. Then execute the final prune pass."""
        if self.prune_level == PruneLevel.LEVEL_0_REMOVE_ALL_EC2:
            self.enis_to_remove = [[eni.file_address for eni in self.enis.values()]]
            self.instances_to_remove = [[instance.file_address for instance in self.instances.values()]]
            return

        self._apply_filters()
        groups = self._prepare_groups()
        self._prune_ifaces_and_instances(groups)

    def write(self):
        """Modifies the Reservations.json and NetworkInterfaces.json to remove
        the identified resources
        """
        # merge the lists of file addresses to remove
        def merge_int_lists(lists: list[list]) -> list[int]:
            merged = []
            for lst in lists:
                new_merged = []
                i, j = 0, 0
                while i < len(merged) and j < len(lst):
                    if merged[i] < lst[j]:
                        new_merged.append(merged[i])
                        i += 1
                    elif merged[i] > lst[j]:
                        new_merged.append(lst[j])
                        j += 1
                    else:
                        new_merged.append(merged[i])
                        i += 1
                        j += 1
                new_merged.extend(merged[i:])
                new_merged.extend(lst[j:])
                merged = new_merged
            return merged

        eni_file_addresses_to_remove = merge_int_lists(self.enis_to_remove)
        instance_file_addresses_to_remove = merge_int_lists(self.instances_to_remove)

        # Modify Reservations.json
        inst_count = 0
        with open(self.dir_aws_config / "Reservations.json.pruner_temp", "w") as fw:
            fw.write("{\n \"Reservations\": [\n")
            with open(self.dir_aws_config / "Reservations.json", "r") as f:
                items = ijson.items(f, 'Reservations.item')
                first = True
                for res_i, item in enumerate(items):
                    instances = []
                    for inst_i, instance in enumerate(item['Instances']):
                        if (res_i, inst_i) in instance_file_addresses_to_remove:
                            continue
                        instances.append(instance)
                        inst_count += 1
                    item['Instances'] = instances

                    if not first:
                        fw.write(",\n")
                    first = False
                    json.dump(item, fw, indent=1, cls=ExtraIndentEncoder)
            fw.write("\n ]\n}\n")

        os.replace(self.dir_aws_config / "Reservations.json.pruner_temp", self.dir_aws_config / "Reservations.json")
        logger.info(f"Wrote pruned Reservations.json, {len(instance_file_addresses_to_remove)} instances removed, {inst_count} remain.")

        # Modify NetworkInterfaces.json
        with open(self.dir_aws_config / "NetworkInterfaces.json", "r") as f:
            data = json.load(f)

        # Modify Reservations.json
        inst_count = 0
        with open(self.dir_aws_config / "NetworkInterfaces.json.pruner_temp", "w") as fw:
            fw.write("{\n \"NetworkInterfaces\": [\n")
            with open(self.dir_aws_config / "NetworkInterfaces.json", "r") as f:
                items = ijson.items(f, 'NetworkInterfaces.item')
                first = True
                for i, item in enumerate(items):
                    if (i,) in eni_file_addresses_to_remove:
                        continue
                    if not first:
                        fw.write(",\n")
                    first = False
                    json.dump(item, fw, indent=1)
                    inst_count += 1
            fw.write("\n ]\n}\n")

        os.replace(self.dir_aws_config / "NetworkInterfaces.json.pruner_temp", self.dir_aws_config / "NetworkInterfaces.json")
        logger.info(f"Wrote pruned NetworkInterfaces.json, {len(eni_file_addresses_to_remove)} interfaces removed, {inst_count} remain.")


class ExtraIndentEncoder(json.JSONEncoder):
    EXTRA_INDENT = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_indent = self.EXTRA_INDENT  # Track current indentation level

    def iterencode(self, o, _one_shot=False):
        """
        Override iterencode to add an extra space at the beginning of each line
        and maintain consistent indentation.
        """

        if isinstance(o, (list, tuple)):
            # Handle lists and tuples (arrays in JSON)
            if not o:  # Check if o is an empty sequence.  This greatly simplifies the handling.
                yield "[]"
                return

            first = True
            self.current_indent += 1
            indent_str = ' ' * self.current_indent
            yield "[\n" + indent_str
            for value in o:
                if not first:
                    yield ",\n" + indent_str
                first = False
                for chunk in self.iterencode(value):
                    yield chunk
            self.current_indent -= 1
            yield "\n" + (' ' * self.current_indent) + "]" # Dedent after closing array

        elif isinstance(o, dict):
            # Handle dictionaries (objects in JSON)
            if not o:  # Handle empty dictionaries
                yield "{}"
                return

            first = True
            self.current_indent += 1  # Increment indent for the object
            indent_str = ' ' * self.current_indent

            yield "{\n" + indent_str # opening bracket with a new line
            for key, value in o.items():
                if not first:
                    yield ",\n" + indent_str  # Comma and newline *before* subsequent items

                first = False
                yield json.encoder.encode_basestring_ascii(key)  # correctly handle strings.
                yield ": "

                for chunk in self.iterencode(value):
                    yield chunk

            self.current_indent -= 1 # Decrement indent after the object
            yield "\n" + (' ' * self.current_indent) + "}"

        elif o is None:
             yield "null"
        elif o is True:
            yield "true"
        elif o is False:
            yield "false"
        elif isinstance(o, int):
            yield str(o)  # Use default integer representation
        elif isinstance(o, float):
            return json.encoder.FLOAT_REPR(o) # Use the default float representation

        elif isinstance(o, str):
            yield json.encoder.encode_basestring_ascii(o)  # Crucial for escaping special chars

        else:
            # Default behavior for other types (e.g., custom classes)
            yield from super().iterencode(o, _one_shot)


def main(aws_config_dir):
    config_path = "config.yaml"
    if not os.path.exists(config_path):
        user_config = UserConfig(prune_level=PruneLevel.LEVEL_1_ONE_EC2_PER_SUBNET)
    else:
        user_config = UserConfig.from_file(config_path)
    if not user_config.enabled:
        logger.info("AWS Pruner is disabled in the config file.")
        return
    aws_prune_tool = AwsPruneTool(
        aws_config_dir,
        user_config.prune_level,
        user_config.filter_exclude,
        user_config.filter_include,
        user_config.group_by,
    )
    aws_prune_tool.load()
    aws_prune_tool.execute()
    aws_prune_tool.write()


if __name__ == "__main__":
    logger.setLevel(logging.INFO)
    logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
    aws_config_dir = sys.argv[1] if len(sys.argv) > 1 else "aws_config"
    main(aws_config_dir)

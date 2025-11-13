import argparse
import datetime
import json
import sys
import uuid
import typing
from attrs import asdict
from rich import print_json
from invariant_client import display
from invariant_client.base_command.base_command import BaseCommand
from invariant_client.pysdk import OutputFormat, RemoteError

if typing.TYPE_CHECKING:
    import argparse

def serialize_networks(inst, field, value):
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    if isinstance(value, uuid.UUID):
        return str(value)
    return value

class NetworkCommand(BaseCommand):
    use_argument_debug = True
    use_argument_group_format = True
    use_argument_format_tsv = True

    target_network: str | None = None

    def __init__(self):
        super().__init__()
        self.network_subcommand: str | None = None
        self.network_name: str | None = None
        self.new_network_name: str | None = None
        self.delete_yes: bool = False

    @classmethod
    def parse_args(cls, subparsers: 'argparse._SubParsersAction[argparse.ArgumentParser]') -> None:
        command_networks = subparsers.add_parser(
            'networks',
            description='List or manage networks.',
            help='List or manage networks.'
        )
        cls._add_common_parser_arguments(command_networks)

        networks_subparsers = command_networks.add_subparsers(
            dest='network_subcommand',
            required=False,
            help='Available subcommands for networks'
        )

        list_parser = networks_subparsers.add_parser(
            'list',
            help='List all networks (default action if no subcommand is given).'
        )
        cls._add_common_parser_arguments(list_parser)

        create_parser = networks_subparsers.add_parser(
            'create',
            help='Create a new network.'
        )
        create_parser.add_argument(
            'network_name',
            help='Name of the network to create.'
        )
        cls._add_common_parser_arguments(create_parser)

        rename_parser = networks_subparsers.add_parser(
            'rename',
            help='Rename an existing network.'
        )
        rename_parser.add_argument(
            'network_name',
            help='Current name of the network.'
        )
        rename_parser.add_argument(
            '--new-name',
            required=True,
            dest='new_name',
            help='New name for the network.'
        )
        cls._add_common_parser_arguments(rename_parser)

        delete_parser = networks_subparsers.add_parser(
            'delete',
            help='Delete a network and all its contents (e.g., snapshots).'
        )
        delete_parser.add_argument(
            'network_name',
            help='Name of the network to delete.'
        )
        delete_parser.add_argument(
            '--yes',
            action='store_true',
            help='Confirm deletion without prompting.'
        )
        cls._add_common_parser_arguments(delete_parser)
        
        command_networks.set_defaults(network_subcommand='list')

    def set_config(self, args: 'argparse.Namespace', env: dict[str, str]) -> None:
        super().set_config(args, env)
        self.network_subcommand = getattr(args, 'network_subcommand', 'list')
        self.network_name = getattr(args, 'network_name', None)
        self.new_network_name = getattr(args, 'new_name', None)
        self.delete_yes = getattr(args, 'yes', False)

    def execute(self) -> None:
        super().execute()

        if self.network_subcommand == 'list':
            networks_response = self.sdk.list_networks()
            networks = [asdict(net, value_serializer=serialize_networks) for net in networks_response.networks]
            if self.format == OutputFormat.JSON:
                print_json(data=networks, default=vars)
            elif self.format == OutputFormat.FAST_JSON:
                print(json.dumps(networks, default=vars))
            else:
                display_table = []
                for net_data in networks:
                    row = {
                        "name": net_data.get("name"),
                        "uuid": net_data.get("uuid"),
                        "comment": net_data.get("comment"),
                        "created_at": net_data.get("created_at"),
                    }
                    display_table.append(row)
                display.print_frame(display_table, self.format)

        elif self.network_subcommand == 'create':
            if not self.network_name:
                raise ValueError("Network name required.")
            self.sdk.create_network(name=self.network_name)
            print(f"Network {self.network_name} created.")

        elif self.network_subcommand == 'rename':
            if not self.network_name or not self.new_network_name:
                raise ValueError("Current network name and new network name are required for rename.")
            self.sdk.rename_network_by_name(network_name=self.network_name, new_name=self.new_network_name)
            print(f"Network {self.network_name} renamed to {self.new_network_name}.")

        elif self.network_subcommand == 'delete':
            if not self.network_name:
                raise ValueError("Network name is required for delete.")
            networks_response = self.sdk.list_networks()
            network_to_delete = None
            for net in networks_response.networks:
                if net.name == self.network_name:
                    network_to_delete = net
                    break
            if not network_to_delete or not network_to_delete.uuid:
                print(f"Network {self.network_name} not found.", file=sys.stderr)
                exit(1)
            num_snapshots = 0
            try:
                snapshots = self.sdk.list_snapshots(filter_net=self.network_name)
                num_snapshots = len(snapshots)
            except RemoteError as e:
                if self.debug:
                    print(f"Could not retrieve snapshots for network {self.network_name}: {e}", file=sys.stderr)
            confirmation_message = f"This will delete network {self.network_name}"
            if num_snapshots > 0:
                confirmation_message += f" and {num_snapshots} snapshot{'s' if num_snapshots > 1 else ''}."
            else:
                confirmation_message += "."
            if not self.delete_yes:
                print(confirmation_message)
                confirm = input("Are you sure (y/n)? ")
                if confirm.lower() != 'y':
                    print("Deletion cancelled.")
                    return
            self.sdk.delete_network(network_uuid=network_to_delete.uuid)
            print(f"Network {self.network_name} deleted.")

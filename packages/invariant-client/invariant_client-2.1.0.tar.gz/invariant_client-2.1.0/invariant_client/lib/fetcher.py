import abc
import datetime
import logging
import os
import pathlib
import random
import shutil
import re
import string
import sys
import textwrap
import tempfile
from dataclasses import dataclass
from typing import Dict, List, Type

import pydantic
import yaml
from netconan import anonymize_files
from netmiko import ConnectHandler, NetmikoTimeoutException

from invariant_client.lib.aws import client as aws_client
from invariant_client.lib.librenms import client as librenms_client
from invariant_client import config
from invariant_client.loaders import load

logger = logging.getLogger(__name__)

class BaseSource(abc.ABC):
    def __init__(self, name):
        self.name = name

    @abc.abstractmethod
    def fetch_data(self):
        pass


class LibreNMSSource(BaseSource):
    fatal = False

    def __init__(self, source_config: config.LibreNMSConfig):
        super().__init__(source_config.name)
        self.hostname = source_config.hostname
        self.device_group = source_config.device_group
        self.user = source_config.ssh_user
        self.fatal = False
        self._temp_dir_manager = None
        if source_config.ssh_key:
            self._temp_dir_manager = tempfile.TemporaryDirectory(prefix="ssh_keys_")
            temp_dir_path = self._temp_dir_manager.name
            self.ssh_key_path = os.path.join(temp_dir_path, "ssh_key")
            with open(self.ssh_key_path, "w", encoding="utf-8") as temp_key_file:
                ssh_key = source_config.ssh_key.get_secret_value()
                ssh_key = self.reformat_pem(ssh_key)
                temp_key_file.write(ssh_key)
            # Set correct permissions
            os.chmod(self.ssh_key_path, 0o600)
            logger.info(f"SSH key content written to secure temporary file: {self.ssh_key_path}")

        elif source_config.ssh_key_path:
            if not os.path.isfile(source_config.ssh_key_path):
                raise FileNotFoundError(
                    f"Provided ssh_key_path does not exist or is not a file: {self.ssh_key_path}"
                )
            self.ssh_key_path = source_config.ssh_key_path
        else:
            raise ValueError(
                f"Source Error for {source_config.name}: No SSH key or path is set in the configuration."
            )

        try:
            self.client = librenms_client.LibreNMSClient(
                self.hostname, source_config.api_key.get_secret_value()
            )
        except ConnectionError as e:
            raise ConnectionError(e)

    def reformat_pem(self, pem_str: str) -> str:
        """
        Take a PEM key string possibly all on one line and
        reformat it into standard PEM format with header,
        base64 data wrapped at 64 chars per line, and footer.
        """
        pem_str = pem_str.strip()

        # This pattern matches the PEM header/footer blocks even if they
        # contain spaces/newlines inside, by being non-greedy up to -----
        pattern = (
            r"(-----BEGIN[^-]*?-----)"  # header: BEGIN + anything (non-greedy) + -----
            r"([\s\S]+?)"  # base64 content (non-greedy)
            r"(-----END[^-]*?-----)"  # footer: END + anything (non-greedy) + -----
        )

        match = re.search(pattern, pem_str, flags=re.DOTALL | re.IGNORECASE)
        if not match:
            raise ValueError("Input does not match expected PEM format")

        header, b64_data, footer = match.groups()
        # Clean base64 data: remove all whitespace/newlines
        b64_data = re.sub(r"\s+", "", b64_data)

        # Wrap base64 data at 64 characters per line
        wrapped = "\n".join(textwrap.wrap(b64_data, 64))

        # Return properly formatted PEM block
        return f"{header.strip()}\n{wrapped}\n{footer.strip()}\n"

    def close(self):
        if self._temp_dir_manager:
            try:
                self._temp_dir_manager.cleanup()  # This removes the directory and its contents
                logger.info(
                    f"Temporary directory {self._temp_dir_manager.name} cleaned up."
                )
            except Exception as e:
                # TemporaryDirectory.cleanup() can sometimes raise errors if files are in use,
                # though usually it's robust.
                print(
                    f"Error cleaning up temporary directory {self._temp_dir_manager.name}: {e}"
                )
            self._temp_dir_manager = None
            self.ssh_key_path = None  # Clear path if it was a temp file

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def _fetch_arista_eos(self, hostname):
        device = {
            "device_type": "arista_eos",
            "host": hostname,
            "username": self.user,
            "use_keys": True,
            "key_file": self.ssh_key_path,
        }
        try:
            net_connect = ConnectHandler(**device)
            net_connect.enable()
            output = net_connect.send_command("show running-config")
            return output

        except NetmikoTimeoutException as e:
            self.fatal = True
            raise ConnectionError(f"Unable to connect to {hostname}: {e}")

    def _fetch_srx(self, hostname):
        device = {
            "device_type": "juniper",
            "host": hostname,
            "username": self.user,
            "use_keys": True,
            "key_file": self.ssh_key_path,
        }
        try:
            net_connect = ConnectHandler(**device)
            net_connect.config_mode()
            output = net_connect.send_command("show")
            return output
        except NetmikoTimeoutException as e:
            self.fatal = True
            raise ConnectionError(f"Unable to connect to {hostname}: {e}")

    def fetch_data(self, path):
        devices = self.client.get_devices_by_group(self.device_group)["devices"]
        # Fetch all IPs to SSH and pull configs from
        for device in devices:

            device_details = self.client.get_device(device["device_id"])["devices"][0]
            os = device_details["os"]
            hostname = device_details["hostname"]
            logger.info(f"Fetching config from {hostname}")
            try:
                if os == "arista_eos":
                    data = self._fetch_arista_eos(hostname)
                elif os == "junos":
                    data = self._fetch_srx(hostname)
                self._write_data(path, hostname, data)
            except ConnectionError as e:
                self.fatal = True
                print(f"Error pulling config from {hostname}: {e}")

    def _write_data(self, path, hostname, data):
        config_dir = pathlib.Path(path) / "configs" / self.name
        config_dir.mkdir(parents=True, exist_ok=True)
        name_with_extension = hostname + ".cfg"
        with open(config_dir / name_with_extension, "w") as f:
            f.write("".join(data))


@dataclass
class AWSSource(BaseSource):
    fatal = False

    def __init__(self, source_config: config.AWSConfig):
        super().__init__(source_config.name)
        self.profile = source_config.profile
        self.role = source_config.role
        self.regions = source_config.regions
        self.accounts = source_config.accounts
        self.ignore_accounts = source_config.ignore_accounts
        self.skip_resources = source_config.skip_resources

    def fetch_data(self, path):
        client = aws_client.AWSClient(
            accounts=self.accounts,
            ignore_accounts=self.ignore_accounts,
            regions=self.regions,
            profile=self.profile,
            role=self.role,
            skip_resources=self.skip_resources,
        )
        self.fatal = client.get_configs(path)


SOURCE_TYPE_TO_CLASS_MAP: Dict[config.SourceKind, Type[BaseSource]] = {
    config.SourceKind.LIBRENMS: LibreNMSSource,
    config.SourceKind.AWS: AWSSource,
    # Add other mappings here
}


class FetchManifest(pydantic.BaseModel):
    created_at: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now,
        description="The timestamp when the fetch was performed."
    )


class Fetcher:
    sources: BaseSource = []

    def _validate_key_type(self, data: Dict, key: str, expected_type: type) -> bool:
        """Validates if a key exists in data and its value is of the expected type."""
        if key not in data:
            logger.error(f"'{key}' is required in the configuration.")
            return False
        if not isinstance(data[key], expected_type):
            logger.error(
                f"'{key}' must be a {expected_type.__name__} but is type {type(data[key]).__name__}"
            )
            return False
        return True

    def __init__(
            self,
            config_path: os.PathLike | str,
            output_path: os.PathLike | str):
        try:
            with open(config_path, "r") as f:
                content = yaml.safe_load(f.read())
                self.config = config.validate_yaml(content)
        except ValueError as e:
            print(e, file=sys.stderr)
            sys.exit(1)
        self.sources: List[BaseSource] = []
        self.output_path = output_path

        if not self.output_path:
            raise ValueError("Required: 'output_path'.")

        for source_config in self.config.sources:
            source_class = SOURCE_TYPE_TO_CLASS_MAP.get(source_config.kind)
            if source_class:
                try:
                    # Pass the specific Pydantic config object to the worker class constructor
                    source_instance = source_class(source_config=source_config)
                    self.sources.append(source_instance)
                except Exception as e:  # Catch broader exceptions during instantiation
                    # The Pydantic model itself is valid, but the class __init__ might fail
                    logger.error(
                        f"Error instantiating source '{source_config.name}' of type '{source_config.kind}': {e}"
                    )
                    # Decide if this is fatal or if you want to continue
            else:
                # This case should ideally not be hit if your SourceType enum
                # and SOURCE_TYPE_TO_CLASS_MAP are comprehensive and TopLevelConfig.sources
                # only allows known types.
                logger.warning(
                    f"Warning: Unknown source type '{source_config.kind}' encountered for source '{source_config.name}'. Skipping."
                )

    def fetch(self):
        print("Starting fetch process")
        with tempfile.TemporaryDirectory() as tempdir:
            unsafe_folder = pathlib.Path(tempdir, "unsafe")
            safe_folder = pathlib.Path(tempdir, "safe")
            for source in self.sources:
                print(f"Fetching source {source.name}")
                source.fetch_data(unsafe_folder)
            if any([source.fatal for source in self.sources]):
                print("Exiting due to errors fetching sources.")
                sys.exit(1)
            if not unsafe_folder.exists():
                print("No data was fetched, exiting.")
                sys.exit(1)
            # https://github.com/intentionet/netconan/blob/master/netconan/anonymize_files.py#L36
            salt = "".join(
                random.choice(string.ascii_letters + string.digits) for _ in range(16)
            )
            anonymize_files.anonymize_files(
                unsafe_folder,
                safe_folder,
                True,  # anonymize passwords
                False,  # anonymize IPs
                salt=salt,
            )
            manifest = FetchManifest().model_dump_json(indent=2)
            safe_folder.joinpath("invariant/").mkdir(parents=True, exist_ok=True)
            safe_folder.joinpath("invariant/.fetch.manifest.json").write_text(manifest)

            output = pathlib.Path(self.output_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            for i in ["aws_configs", "configs"]:
                try:
                    shutil.rmtree(output.joinpath(i))
                except:
                    pass
            shutil.copytree(safe_folder, output, dirs_exist_ok=True)
        print(f"Done fetching output to {output}")

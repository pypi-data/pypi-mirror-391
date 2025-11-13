import importlib
import ssl
from invariant_client.base_command.base_command import BaseCommand

import typing

from invariant_client.version import VersionClient
if typing.TYPE_CHECKING:
    import argparse


class VersionCommand(BaseCommand):
    needs_authn = False
    use_argument_debug = True

    @classmethod
    def parse_args(cls, subparsers: 'argparse._SubParsersAction[argparse.ArgumentParser]') -> None:
        command_version   = subparsers.add_parser(
            'version',
            description='Display the client and server versions.',
            help="Display the client and server versions.")

        cls._add_common_parser_arguments(command_version)

    def set_config(self, args: 'argparse.Namespace', env: dict[str, str]) -> None:
        super().set_config(args, env)

    def execute(self):
        super().execute()
        client_version: str = importlib.resources.read_text("invariant_client", "VERSION", encoding='utf-8')
        print(f"client: {client_version.strip()}")
        print(f"server: {VersionClient(self.invariant_domain, ssl.create_default_context()).get_version()}")

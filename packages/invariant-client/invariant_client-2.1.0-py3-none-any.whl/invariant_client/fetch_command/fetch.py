import typing

from invariant_client.base_command.base_command import BaseCommand

if typing.TYPE_CHECKING:
    import argparse


class FetchCommand(BaseCommand):
    use_argument_debug = True

    config_path: str | None = None

    @classmethod
    def parse_args(cls, subparsers: 'argparse._SubParsersAction[argparse.ArgumentParser]') -> None:
        command_fetch = subparsers.add_parser(
            'fetch',
            help='Fetch network configs from remote sources to disk.'
        )
        cls._add_common_parser_arguments(command_fetch)

        command_fetch.add_argument(
            'fetch_config',
            nargs='?',
            metavar='config_file',
            default='./invariant_config.yaml',
            help='Fetch configuration file. Configure sources like LibreNMS, AWS, and indicate where and how to find credentials. Default is invariant_config.yaml.'
        )

        command_fetch.add_argument(
            '--output',
            dest='output_path',
            metavar='OUTPUT_PATH',
            help='Download and anonymize configs to a local dir.',
            required=True,
        )

    def set_config(self, args: 'argparse.Namespace', env: dict[str, str]) -> None:
        super().set_config(args, env)
        self.config_path = args.fetch_config
        self.output_path = args.output_path

    def execute(self):
        super().execute()
        self.sdk.fetch(self.config_path, output_path=self.output_path)

from contextlib import contextmanager
import tempfile
import typing

from invariant_client.run_command.run import RunCommand

if typing.TYPE_CHECKING:
    import argparse


class SyncCommand(RunCommand):
    use_argument_debug = True

    config_path: str | None = None

    @classmethod
    def parse_args(cls, subparsers: 'argparse._SubParsersAction[argparse.ArgumentParser]') -> None:
        command_sync = subparsers.add_parser(
            'sync',
            description='Update the target Invariant network from remote sources.',
            help='Update the target Invariant network from remote sources.'
        )
        cls._add_common_parser_arguments(command_sync)

        command_sync.add_argument(
            'fetch_config',
            nargs='?',
            metavar='config_file',
            default='./invariant_config.yaml',
            help='Fetch configuration file. Configure sources like LibreNMS, AWS, and indicate where and how to find credentials. Default is invariant_config.yaml.'
        )

        command_sync.add_argument(
            '--network',
            dest='network',
            help='The target network to update.',
            required=True,
        )

        command_sync.add_argument(
            '--role',
            dest='role',
            help='The snapshot role for this snapshot, e.g. "live", "intended".',
        )

        command_sync.add_argument(
            '--output',
            dest='output_path',
            metavar='OUTPUT_PATH',
            help='Also write anonymized configs to a local dir.',
        )

        command_sync.add_argument(
            '--aws-pruner',
            dest='aws_pruner',
            action='store_true',
            help='Activate the AWS pruner.'
        )

        command_sync.add_argument(
            '--aws-pruner-dry-run', '--no-aws-pruner',
            dest='no_aws_pruner',
            action='store_true',
            help='AWS pruner runs in dry-run only. Combine with aws-pruner-debug-out to see the would-be pruned snapshot.',
        )

        command_sync.add_argument(
            '--aws-pruner-debug-out',
            nargs='?',
            dest='aws_pruner_output_directory',
            metavar="DIR",
            const='./aws_pruner_debug',  # Value when --aws-pruner-debug-out is present but has no value
            default=None,  # Value when --aws-pruner-debug-out is NOT present
            help='Specify a directory to write the pruned snapshot for preview purposes. Default is ./aws_pruner_debug/ . Performs a dry-run if --no-aws-pruner is set or the pruner is disabled in aws_pruner.yaml .'
        )

        command_sync.add_argument(
            '--no-upload-limit',
            dest='no_upload_limit',
            action='store_true',
            help='Disable the 40MB upload limit for snapshots.',
        )

        command_sync.add_argument(
            '--no-wait',
            dest='no_wait',
            action='store_true',
            help='Start the Invariant analysis and exit.',
        )

    def set_config(self, args: 'argparse.Namespace', env: dict[str, str]) -> None:
        super().set_config(args, env)
        self.config_path = args.fetch_config
        self.output_path = args.output_path
        self.no_upload_limit = getattr(args, 'no_upload_limit', False)
        self.aws_pruner_output_directory = getattr(args, 'aws_pruner_output_directory')
        self.aws_pruner = getattr(args, 'aws_pruner')
        self.no_aws_pruner = getattr(args, 'no_aws_pruner')
        self.no_wait = getattr(args, 'no_wait')

    @contextmanager
    def _output_path(self) -> str:
        if self.output_path:
            yield self.output_path
        else:
            with tempfile.TemporaryDirectory(prefix="invariant_sync_workdir_") as workdir:
                yield workdir

    def execute(self):
        with self._output_path() as output_path:
            self.sdk.fetch(self.config_path, output_path=output_path)

            # Pass to RunCommand.execute
            self.target = output_path
            super().execute()

from contextlib import contextmanager
import datetime
import io
import json
import logging
import os
import pathlib
import platform
import random
import shutil
import string
import sys
import tempfile
import time
import typing

import backoff
from netconan import anonymize_files
from rich import print_json

from invariant_client import pysdk, zip_util
from invariant_client import display
from invariant_client.aws_pruner.aws_pruner_integration import use_aws_pruner
from invariant_client.base_command.base_command import BaseCommand
from invariant_client.lib.fetcher import FetchManifest
from invariant_client.pysdk import OutputFormat

if typing.TYPE_CHECKING:
    import argparse


logger = logging.getLogger(__name__)


def get_home_directory() -> pathlib.Path:
    """Tries various methods to determine the user's home directory, defaulting to the current working directory."""
    try:
        return pathlib.Path.home()
    except RuntimeError:
        pass

    if platform.system() == 'Windows':
        try:
            return pathlib.Path(os.environ['HOMEDRIVE'], os.environ['HOMEPATH'])
        except KeyError:
            pass

    try:
        return pathlib.Path(os.environ['HOME'])
    except RuntimeError:
        pass

    try:
        return pathlib.Path(os.environ['LAMBDA_TASK_ROOT'])
    except KeyError:
        pass

    return pathlib.Path.cwd()


class RunCommand(BaseCommand):
    use_argument_debug = True
    use_argument_group_format = True
    use_argument_format_condensed = True
    # No TSV format for this command

    @classmethod
    def parse_args(cls, subparsers: 'argparse._SubParsersAction[argparse.ArgumentParser]') -> None:
        command_run = subparsers.add_parser(
            'run',
            description='Analyze the current snapshot.',
            help="Analyze the current snapshot.")

        cls._add_common_parser_arguments(command_run)

        command_run.add_argument(
            '--compare-to',
            dest='compare_to',
            help='Compare this snapshot to another by its git ref. Ref must refer to the primary git repository.',
        )

        command_run.add_argument(
            '--target',
            dest='target',
            help='An Invariant project root directory. Default is current directory.',
        )

        command_run.add_argument(
            '--network',
            dest='network',
            help='The name of the network being evaluated.',
        )

        command_run.add_argument(
            '--role',
            dest='role',
            help='The network role being evaluated, e.g. "live", "intended".',
        )

        # AWS Pruner:
        # The pruner will run if invariant/aws_pruner.yaml exists in the snapshot directory or if --aws-pruner flag is present.
        # The user can disable the pruner with --no-aws-pruner or enabled: False in the config.
        # The user can set --aws-pruner-preview=<dir> to write the pruned snapshot to a directory. It can be combined with --no-aws-pruner or enabled: False .
        # The pruner will write the pruned snapshot to a tempdir and not modify the original.
        command_run.add_argument(
            '--aws-pruner',
            dest='aws_pruner',
            action='store_true',
            help='Activate the AWS pruner.'
        )

        command_run.add_argument(
            '--aws-pruner-dry-run', '--no-aws-pruner',
            dest='no_aws_pruner',
            action='store_true',
            help='AWS pruner runs in dry-run only. Combine with aws-pruner-debug-out to see the would-be pruned snapshot.',
        )

        command_run.add_argument(
            '--aws-pruner-debug-out',
            nargs='?',
            dest='aws_pruner_output_directory',
            const='./aws_pruner_debug',  # Value when --aws-pruner-debug-out is present but has no value
            default=None,  # Value when --aws-pruner-debug-out is NOT present
            help='Specify a directory to write the pruned snapshot for preview purposes. Default is ./aws_pruner_debug/ . Performs a dry-run if --no-aws-pruner is set or the pruner is disabled in aws_pruner.yaml .'
        )

        command_run.add_argument(
            '--no-upload-limit',
            dest='no_upload_limit',
            action='store_true',
            help='Disable the 40MB upload limit for snapshots.',
        )

        command_run.add_argument(
            '--no-wait',
            dest='no_wait',
            action='store_true',
            help='Start the Invariant analysis and exit.',
        )

    def set_config(self, args: 'argparse.Namespace', env: dict[str, str]) -> None:
        super().set_config(args, env)
        self.target = getattr(args, 'target', None) or '.'
        self.network = getattr(args, 'network') or ''
        self.no_upload_limit = getattr(args, 'no_upload_limit', False)
        self.aws_pruner_output_directory = getattr(args, 'aws_pruner_output_directory')
        self.aws_pruner = getattr(args, 'aws_pruner')
        self.no_aws_pruner = getattr(args, 'no_aws_pruner')
        self.no_wait = getattr(args, 'no_wait')

    def execute(self):
        super().execute()

        bytes = None
        if pathlib.Path(self.target).is_file():
            with open(self.target, "rb") as f:
                bytes = io.BytesIO(f.read())
        elif pathlib.Path(self.target).is_dir():
            if not pathlib.Path(self.target, 'configs').is_dir() and not pathlib.Path(self.target, 'aws_configs').is_dir():
                print(f"Invalid directory. Expected subdirectories 'configs' or 'aws_configs' to be present. See https://docs.invariant.tech/Reference/Snapshots for instructions.", file=sys.stderr)
                exit(1)

            home_dir = get_home_directory()
            if pathlib.Path(self.target).absolute() == pathlib.Path(home_dir).absolute():
                print("Upload aborted. Cowardly refusing to upload your home directory.")
                exit(1)

            BYTES_LIMIT = 40000000
            if self.no_upload_limit:
                BYTES_LIMIT = 0

            bytes = io.BytesIO()
            zip_created = False
            if (
                pathlib.Path(self.target, 'aws_configs').is_dir() and \
                (
                    pathlib.Path(self.target, 'invariant', 'aws_pruner.yaml').exists() or \
                    self.aws_pruner or \
                    self.aws_pruner_output_directory
                )
            ):
                with tempfile.TemporaryDirectory() as tempdir:
                    workdir = pathlib.Path(tempdir, pathlib.Path(self.target).absolute().name)
                    shutil.copytree(self.target, workdir)

                    print("Pruner starting...")

                    pruner_debug_target = pathlib.Path(self.target, self.aws_pruner_output_directory) if self.aws_pruner_output_directory else None
                    apply_pruner = use_aws_pruner(workdir, self.no_aws_pruner, pruner_debug_target)
                    if apply_pruner:
                        # Create a new zipfile from the pruned snapshot in the tempdir, discarding the original
                        with anonymized(workdir) as safe_sourcedir:
                            bytes = io.BytesIO()
                            zip_util.zip_dir(safe_sourcedir, bytes, BYTES_LIMIT)
                            zip_created = True
                    else:
                        print(f"Pruner changes discarded (dry run).")

            if not zip_created:
                with anonymized(self.target) as safe_sourcedir:
                    zip_util.zip_dir(safe_sourcedir, bytes, BYTES_LIMIT)  # Write a zip file into 'bytes'
                    zip_created = True
        else:
            print("Unacceptable target", file=sys.stderr)
            print(str(self.target), file=sys.stderr)
            exit(1)

        # Not implemented
        compare_to = None
        role = None

        try:
            exec_uuid = upload_snapshot(self.sdk, bytes, compare_to, self.network, role, self.format)
        except KeyboardInterrupt as e:
            print("Exiting...", file=sys.stderr)
            exit(1)

        if self.format == OutputFormat.TABULATE:
            print("Analysis complete.")
        response = self.sdk.report_detail(exec_uuid)
        # pprint.pprint(asdict(response), width=200)
        if self.format == OutputFormat.JSON or self.format == OutputFormat.FAST_JSON:
            response_json = json.dumps(response.to_dict(), sort_keys=True)
            try:
                print_json(response_json)
            except:
                print(response_json)
        elif self.format == OutputFormat.CONDENSED:
            if response.status['state'] != 'COMPLETE':
                if response.summary['errors'] > 0:
                    errors_locator = response.report.reports.errors
                    errors_response = self.sdk.snapshot_file(errors_locator)
                    display.snapshot_errors(errors_response, self.format)
            display.snapshot_condensed_status(response)
        else:
            display.snapshot_status(response)
            if response.status['state'] == 'COMPLETE':
                display.snapshot_halted(response)
                print('')
                summary = self.sdk.report_detail_text(str(exec_uuid), json_mode=False)
                if summary.text:
                    print(summary.text)
                else:
                    display.snapshot_summary_table(response, self.format)

                print(f"\nRun 'invariant show <file>' to examine any file.")

                if response.summary['errors'] > 0:
                    print(f"\n{response.summary['errors']} {'error' if response.summary['errors'] == 1 else 'errors'} found.")
                    errors_locator = response.report.reports.errors
                    errors_response = self.sdk.snapshot_file(errors_locator)
                    display.snapshot_errors(errors_response, self.format)

            else:
                if response.summary['errors'] > 0:
                    errors_locator = response.report.reports.errors
                    errors_response = self.sdk.snapshot_file(errors_locator)
                    display.snapshot_errors(errors_response, self.format)


@contextmanager
def anonymized(input_path: str | pathlib.Path):
    use_anonymizer = not pathlib.Path(input_path, 'invariant/.fetch.manifest.json').exists()
    if not use_anonymizer:
        yield input_path
        return

    with tempfile.TemporaryDirectory() as temp_path:
        unsafe_path = pathlib.Path(temp_path, 'unsafe')
        safe_path = pathlib.Path(temp_path, 'safe')
        for dir_name in ['aws_configs', 'batfish', 'configs', 'def', 'hosts', 'invariant']:
            input_dir = pathlib.Path(input_path, dir_name)
            unsafe_dir = pathlib.Path(unsafe_path, dir_name)
            if input_dir.exists():
                shutil.copytree(input_dir, unsafe_dir)

        # https://github.com/intentionet/netconan/blob/master/netconan/anonymize_files.py#L36
        salt = "".join(
            random.choice(string.ascii_letters + string.digits) for _ in range(16)
        )
        anonymize_files.anonymize_files(
            unsafe_path,
            safe_path,
            True,  # anonymize passwords
            False,  # anonymize IPs
            salt=salt,
        )
        manifest = FetchManifest().model_dump_json(indent=2)
        pathlib.Path(safe_path, "invariant/").mkdir(parents=True, exist_ok=True)
        pathlib.Path(safe_path, "invariant/.fetch.manifest.json").write_text(manifest)
        yield safe_path


DEFAULT_RETRY_SECONDS = 3


class UploadTerminationError(Exception):
    """An exception that is raised when a snapshot upload is terminated."""

    def __init__(self, *args, retry_after: int):
        super().__init__(self, *args)
        self.retry_after = retry_after


@backoff.on_exception(
        backoff.runtime,
        UploadTerminationError,
        value=lambda e: e.retry_after + random.uniform(0, e.retry_after),
        jitter=None,
        logger=None,
        on_backoff=lambda _: logger.warning('Upload was remotely terminated, retrying...'),
        max_tries=3)
def upload_snapshot(sdk: pysdk.Invariant, bytes: io.BytesIO, compare_to: str, network: str, role: str, format: OutputFormat, no_wait: bool = False) -> str:
    if format == OutputFormat.TABULATE:
        print("Uploading snapshot...")
    exec_uuid = sdk.upload_snapshot(
        source=bytes,
        network=network,
        role=role,
        compare_to=compare_to)
    exec_uuid = exec_uuid.exec_uuid

    if format == OutputFormat.TABULATE:
        print(f"Processing... ({exec_uuid})")
    elif format == OutputFormat.CONDENSED:
        print(f"snapshot: {exec_uuid}")

    if no_wait:
        if format == OutputFormat.TABULATE:
            print("Analysis started in --no_wait mode")
        elif format == OutputFormat.CONDENSED:
            print(f"outcome: started")
        return exec_uuid

    end_time = datetime.datetime.now() + datetime.timedelta(weeks=1)
    while datetime.datetime.now() < end_time:
        response = sdk.upload_is_running(exec_uuid)
        if response.terminated:
            raise UploadTerminationError(f"Upload was remotely terminated, try again later", retry_after=response.retry_after_seconds or DEFAULT_RETRY_SECONDS)
        if not response.is_running:
            break

        # TODO send some RetryAfter header to control this
        # TODO separately, exponential back-off on error
        time.sleep(4)
    if not response:
        print("Timed out.", file=sys.stderr)
        exit(1)
    return exec_uuid
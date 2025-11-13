import sys
import uuid

from rich import print_json
from invariant_client import display
from invariant_client.base_command.base_command import BaseCommand

import typing

from invariant_client.bindings.invariant_instance_client.models.file_index import FileIndex
from invariant_client.bindings.invariant_instance_client.models.snapshot_report_data import SnapshotReportData
from invariant_client.pysdk import OutputFormat
if typing.TYPE_CHECKING:
    import argparse


class ShowCommand(BaseCommand):
    use_argument_debug = True
    use_argument_group_format = True
    use_argument_format_tsv = True
    use_argument_format_condensed = True

    @classmethod
    def parse_args(cls, subparsers: 'argparse._SubParsersAction[argparse.ArgumentParser]') -> None:
        command_show = subparsers.add_parser(
            'show',
            description='Access network snapshot analysis results.',
            help="Access network snapshot analysis results.")

        cls._add_common_parser_arguments(command_show)

        command_show.add_argument(
            'file_name',
            nargs="?",
            help='The snapshot file to examine.'
        )

        command_show.add_argument(
            '--snapshot',
            dest='snapshot_name',
            help='The snapshot to examine. If unset, environment variable INVARIANT_SNAPSHOT is used.'
        )

    def set_config(self, args: 'argparse.Namespace', env: dict[str, str]) -> None:
        super().set_config(args, env)
        env_snapshot = env.get('INVARIANT_SNAPSHOT', None)
        self.snapshot_name = args.snapshot_name
        if not self.snapshot_name:
            self.snapshot_name = env_snapshot
        self.file_name = args.file_name

    def execute(self):
        super().execute()
        snapshot_name = self.snapshot_name
        if not snapshot_name:
            # NOTE: API Token users should explicitly set --snapshot or INVARIANT_SNAPSHOT
            last_snapshot = self.sdk.list_reports(filter_session=True, limit=1)
            if not last_snapshot or len(last_snapshot.reports) == 0:
                raise ValueError(f"Use --snapshot <name> argument or INVARIANT_SNAPSHOT environment variable to select a snapshot.")
            snapshot_name = last_snapshot.reports[0].uuid

        if isinstance(snapshot_name, uuid.UUID):
            exec_uuid = snapshot_name
        else:
            try:
                exec_uuid = uuid.UUID(snapshot_name, version=4)
            except ValueError as e:
                raise ValueError(f"Expected {snapshot_name} to be a UUID like f5b4e387-e336-499e-b3a0-d6186c590572.") from e

        if self.file_name is not None:
            # Access a specific file
            try:
                file = uuid.UUID(self.file_name, version=4)
            except ValueError:
                # OK if the file is the file key (e.g. errors)
                file = self.file_name
            if not isinstance(file, uuid.UUID):
                # Resolve non-UUID file to UUID
                response = self.sdk.report_detail(exec_uuid)
                reports = response.report.reports
                try:
                    if isinstance(reports, SnapshotReportData):
                        try:
                            file_locator = reports.files[file]
                        except KeyError as e:
                            if file == 'files':
                                raise
                            # Metafile
                            file_locator: FileIndex | uuid.UUID = getattr(reports, file)
                    else:
                        file_locator: uuid.UUID = getattr(reports, file)
                except (KeyError, AttributeError) as e:
                    raise ValueError(f"Report {file} not found for snapshot {exec_uuid}.") from e

            if self.format == OutputFormat.JSON or self.format == OutputFormat.FAST_JSON:
                file_data = self.sdk.snapshot_file(file_locator)
                if self.format == OutputFormat.JSON:
                    print_json(file_data.to_json(orient='records'))
                elif self.format == OutputFormat.FAST_JSON:
                    print(file_data.to_json(orient='records'))

            elif self.format == OutputFormat.TSV:
                file_data = self.sdk.snapshot_file(file_locator)
                display.print_frame(file_data, self.format)
            else:
                file_data = self.sdk.snapshot_file(file_locator)
                display.print_frame(file_data, self.format)
                # print("Set --traces to display all example traces")
                print("Set --json to get JSON")
                print("See 'show --help' for more options")

        else:
            # Display the process summary for the snapshot
            if self.format == OutputFormat.TABULATE:
                print(f"Snapshot {exec_uuid}")
            elif self.format == OutputFormat.CONDENSED:
                print(f"snapshot: {exec_uuid}")
            response = self.sdk.report_detail(str(exec_uuid))
            if self.format == OutputFormat.TABULATE:
                display.snapshot_status(response)
            if self.format == OutputFormat.CONDENSED:
                if response.status['state'] != 'COMPLETE':
                    if response.summary['errors'] > 0:
                        errors_locator = response.report.reports.errors
                        errors_response = self.sdk.snapshot_file(errors_locator)
                        display.snapshot_errors(errors_response, self.format)
                display.snapshot_condensed_status(response)
            elif response.status['state'] == 'COMPLETE':
                if self.format == OutputFormat.TABULATE:
                    display.snapshot_halted(response)
                    print('')
                    summary = self.sdk.report_detail_text(str(exec_uuid), json_mode=False)
                    if summary.text:
                        print(summary.text)
                    else:
                        display.snapshot_summary_table(response, self.format)
                elif self.format == OutputFormat.JSON or self.format == OutputFormat.FAST_JSON:
                    summary = self.sdk.report_detail_text(str(exec_uuid), json_mode=True)
                    if summary.json:
                        if self.format == OutputFormat.JSON:
                            try:
                                print_json(summary.json)
                            except:
                                print(summary.json)
                        elif self.format == OutputFormat.FAST_JSON:
                            print(summary.json)
                    else:
                        display.snapshot_summary_table(response, self.format)
                else:
                    display.snapshot_summary_table(response, self.format)
                if self.format == OutputFormat.TABULATE:
                    print(f"\nRun 'invariant show <file>' to examine any file.")

                    if response.summary['errors'] > 0:
                        print(f"\n{response.summary['errors']} {'error' if response.summary['errors'] == 1 else 'errors'} found.", file=sys.stderr)
                        errors_locator = response.report.reports.errors
                        errors_response = self.sdk.snapshot_file(errors_locator)
                        display.snapshot_errors(errors_response, self.format)
            elif response.summary['errors'] > 0:
                errors_locator = response.report.reports.errors
                errors_response = self.sdk.snapshot_file(errors_locator)
                display.snapshot_errors(errors_response, self.format)

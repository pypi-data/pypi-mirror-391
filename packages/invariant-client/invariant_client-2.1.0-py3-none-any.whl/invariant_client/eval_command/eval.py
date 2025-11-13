import argparse
import base64
import io
import json
import logging
import pathlib
import re
import sys
import typing
import uuid

from attrs import asdict
import yaml
from dateutil import parser, tz
from rich import print_json
from rich.console import Console
from rich.syntax import Syntax

from invariant_client import display, pysdk, zip_util
from invariant_client.base_command.base_command import BaseCommand
from invariant_client.bindings.invariant_instance_client.models import ExecResponse
from invariant_client.pysdk import OutputFormat
from invariant_client.eval_command.pick_rule import pick_rule
import time


logger = logging.getLogger(__name__)


# Helper type for flattened rules
FlattenedRule = typing.Tuple[str, int, dict] # (policy_name, rule_index, rule_dict)


class EvalCommand(BaseCommand):
    needs_authn = True
    use_argument_debug = True
    use_argument_group_format = True
    use_argument_format_tsv = True
    use_argument_format_condensed = True

    snapshot_uuid: uuid.UUID | None = None
    target: pathlib.Path = pathlib.Path('.')
    rule_file_path: pathlib.Path | None = None
    rule_selector: str | None = None

    @classmethod
    def parse_args(cls, subparsers: 'argparse._SubParsersAction[argparse.ArgumentParser]') -> None:
        command_try_rule = subparsers.add_parser(
            'eval',
            description='Test a single rule against an existing snapshot.',
            help="Test a single access policy rule.")

        cls._add_common_parser_arguments(command_try_rule)

        snapshot_group = command_try_rule.add_mutually_exclusive_group(required=False)
        snapshot_group.add_argument(
            '--snapshot',
            dest='snapshot_uuid',
            help='Specify the snapshot context: a snapshot UUID or a network name (uses latest).',
        )
        snapshot_group.add_argument(
            '--network',
            dest='network_name',
            help='Use the latest snapshot uploaded in the current CLI session.',
        )

        command_try_rule.add_argument(
            '--target',
            dest='target',
            type=pathlib.Path,
            default='.',
            help='An Invariant project root directory containing defs/ and invariant/locations/. Default is current directory.',
        )

        command_try_rule.add_argument(
            '--rule-file',
            dest='rule_file_path',
            type=pathlib.Path,
            required=True,
            help='Path to the YAML file containing the rule to try.',
        )

        command_try_rule.add_argument(
            '--rule',
            dest='rule_selector',
            help='Specify the target rule if --rule-file contains more than one. Format: <policy_name>[<rule_index>] or <global_rule_index>.',
        )

    def set_config(self, args: 'argparse.Namespace', env: dict[str, str]) -> None:
        super().set_config(args, env)
        self.network_name = None
        self.snapshot_uuid = None
        if args.snapshot_uuid:
            self.snapshot_uuid = uuid.UUID(args.snapshot_uuid)
        elif env.get('INVARIANT_SNAPSHOT', None) is not None:
            self.snapshot_uuid = uuid.UUID(env.get('INVARIANT_SNAPSHOT'))
        elif args.network_name:
            self.network_name = args.network_name

        self.target = pathlib.Path(args.target) if args.target is not None else None
        self.rule_file_path = pathlib.Path(args.rule_file_path) if args.rule_file_path is not None else None
        self.rule_selector = args.rule_selector

        if not self.rule_file_path or not self.rule_file_path.is_file():
             raise FileNotFoundError(f"Rule file not found: {self.rule_file_path}")

        if not self.target or not self.target.is_dir():
             raise FileNotFoundError(f"Target not found: {self.target}")


    def _resolve_snapshot_context(self) -> uuid.UUID:
        """Resolves user input into a specific snapshot UUID."""
        if self.snapshot_uuid is None and self.network_name is None:
            # Look up the most recent snapshot for this session
            snapshots_response = self.sdk.list_snapshots(filter_session=True, limit=1)
            if len(snapshots_response) == 0:
                print("No snapshots found for the current session. Please use --network or --snapshot .", file=sys.stderr)
                exit(1)
            snapshot_model = snapshots_response[0].snapshot
            print(f"Using snapshot {snapshot_model.uuid} (uploaded from this session)", file=sys.stderr)
            return snapshot_model.uuid
        elif self.snapshot_uuid is not None:
            # Direct snapshot UUID provided
            return self.snapshot_uuid
        else:
            # Look up the latest snapshot for the specified network name
            snapshots_response = self.sdk.list_snapshots(filter_net=self.network_name, limit=1)
            if len(snapshots_response) == 0:
                print(f"No snapshots found for network {self.network_name}.", file=sys.stderr)
                exit(1)
            snapshot_model = snapshots_response[0].snapshot
            print(f"Using snapshot {snapshot_model.uuid} (latest for network {self.network_name})", file=sys.stderr)
            return snapshot_model.uuid

    def _zip_and_encode(self, directory_path: pathlib.Path) -> str:
        """Zips directory contents in memory and returns base64 encoded string."""
        if not directory_path.is_dir():
            logger.warning(f"Directory not found for zipping: {directory_path}. Skipping.")
            return "" # Return empty string for non-existent directories
        buffer = io.BytesIO()
        try:
            # Assuming zip_util handles empty directories gracefully
            zip_util.zip_dir(str(directory_path), buffer)
            buffer.seek(0)
            zip_content = buffer.read()
            return base64.b64encode(zip_content).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to zip directory '{directory_path}'", exc_info=e)
            raise RuntimeError(f"Could not process directory: {directory_path}") from e

    def _display_results(
        self,
        response: ExecResponse,
        tested_rule_str: str
        ):
        """Formats and prints the ExecResponse."""

        # Handle Condensed output
        if self.format == OutputFormat.CONDENSED:
            try:
                # A bit naive, assumes violations exist if keys are present and non-empty
                violations_found = False
                for key in ["policy_violations", "critical_flows_violations"]:
                    if key in response.results:
                        # The result is a JSON string representing a list of dicts
                        result_list = json.loads(response.results[key])
                        if isinstance(result_list, list) and len(result_list) > 0:
                             violations_found = True
                             break
                if violations_found:
                    print("FAIL")
                else:
                    # TODO: How does the API indicate an execution error vs. just no violations?
                    # Assuming for now that if no violations, it passed.
                    print("PASS")
            except Exception as e:
                logger.error("Error parsing condensed results", exc_info=e)
                print("ERROR")
            return

        # Handle JSON output first
        # if self.format in (OutputFormat.JSON, OutputFormat.FAST_JSON):
        else:
            output_data = asdict(response)
            try:
                reports = output_data['results'] = output_data['results']['additional_properties']
                parsed_reports = {}
                for key in reports.keys():
                    parsed_reports[key] = json.loads(reports[key])
                output_data['results'] = parsed_reports
            except:
                pass

            try:
                output_data['result_files'] = output_data['result_files']['additional_properties']
            except:
                pass

            if self.format == OutputFormat.FAST_JSON:
                print(json.dumps(output_data, default=str))
            else:
                print_json(json.dumps(output_data, default=str))
            return


    def execute(self) -> None:
        super().execute()
        try:
            resolved_snapshot_uuid = self._resolve_snapshot_context()

            rule_str = pick_rule(self.rule_file_path, self.rule_selector)
            locs_b64 = self._zip_and_encode(self.target.resolve() / 'invariant' / 'locations')
            defs_b64 = self._zip_and_encode(self.target.resolve() / 'def')

            print(f"Trying rule '{self.rule_selector}' from {self.rule_file_path.name} ...", file=sys.stderr)
            # measure the time of try_rule
            start_time = time.time()
            response = self.sdk.try_rule(
                snapshot_uuid=str(resolved_snapshot_uuid),
                rule=rule_str,
                locations=locs_b64,
                defs=defs_b64
            )
            elapsed_time = time.time() - start_time
            print(f"Elapsed time: {elapsed_time:.2f} seconds", file=sys.stderr)
            self._display_results(response, rule_str)

        except (ValueError, FileNotFoundError, yaml.YAMLError, pysdk.RemoteError, pysdk.AuthorizationException) as e:
            print(f"Error: {e}", file=sys.stderr)
            if self.debug:
                logger.exception("Error during try-rule execution")
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e}", file=sys.stderr)
            if self.debug:
                logger.exception("Unexpected error during try-rule execution")
            sys.exit(1)

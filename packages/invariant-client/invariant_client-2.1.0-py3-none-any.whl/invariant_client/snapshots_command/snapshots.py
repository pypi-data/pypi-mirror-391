import datetime
import json
import uuid
from attrs import asdict
from rich import print_json
from invariant_client import display
from invariant_client.base_command.base_command import BaseCommand

import typing

from invariant_client.pysdk import OutputFormat
if typing.TYPE_CHECKING:
    import argparse


def serialize(inst, field, value):
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    if isinstance(value, uuid.UUID):
        return str(value)
    return value


class SnapshotsCommand(BaseCommand):
    use_argument_debug = True
    use_argument_group_format = True
    use_argument_format_tsv = True
    # No condensed format for this command

    snapshot_uuid: uuid.UUID | None = None

    @classmethod
    def parse_args(cls, subparsers: 'argparse._SubParsersAction[argparse.ArgumentParser]') -> None:
        import argparse  # Ensure argparse is imported here for SUPPRESS
        command_snapshots = subparsers.add_parser(
            'snapshots',
            description='List or manage your network snapshots.',
            help="List or manage your network snapshots.",
        )

        inner_subparsers = command_snapshots.add_subparsers(dest='subcommand')

        command_list = inner_subparsers.add_parser('list', help='List snapshots (default).')
        command_move = inner_subparsers.add_parser('move', help='Move a snapshot between networks.')
        command_delete = inner_subparsers.add_parser('delete', help='Delete a snapshot.')

        cls._add_common_parser_arguments(command_list)
        cls._add_common_parser_arguments(command_move)
        cls._add_common_parser_arguments(command_delete)

        command_move.add_argument(
            'snapshot_uuid',
            help='UUID of the snapshot to move between networks.'
        )

        command_move.add_argument(
            '--to-network',
            metavar='NETWORK',
            dest='move_network_name',
            help='Target network name.'
        )

        command_delete.add_argument(
            'snapshot_uuid',
            help='UUID of the snapshot to delete.'
        )

        command_list.add_argument(
            '--network',
            dest='network',
            help='Filter snapshots by network.',
            default="default"
        )

        command_list.add_argument(
            '--role',
            dest='role',
            help='Filter by network role being evaluated, e.g. "live", "intended".',
        )

        cls._add_common_parser_arguments(command_snapshots)

        command_snapshots.add_argument(
            '--network',
            dest='network',
            help='Filter snapshots by network.',
            default="default"
        )

        command_snapshots.add_argument(
            '--role',
            dest='role',
            help='Filter by network role being evaluated, e.g. "live", "intended".',
        )

    def set_config(self, args: 'argparse.Namespace', env: dict[str, str]) -> None:
        super().set_config(args, env)
        self.subcommand = getattr(args, 'subcommand', None)
        self.network = getattr(args, 'network', None)
        snapshot_uuid = getattr(args, 'snapshot_uuid', None)
        self.move_to = getattr(args, 'move_network_name', None)

        if self.subcommand == 'move' or self.subcommand == 'delete':
            if snapshot_uuid is None:
                raise ValueError("Option <snapshot_uuid> is required for move and delete subcommands.")
            try:
                self.snapshot_uuid = uuid.UUID(snapshot_uuid, version=4)
            except ValueError as e:
                raise ValueError(f"Expected {snapshot_uuid} to be a UUID.") from e

            if self.network is not None:
                raise ValueError("Option --network is allowed only when listing snapshots.")


    def execute(self):
        super().execute()

        if self.subcommand == 'move':
            if self.move_to is None:
                raise ValueError("Option --to-network is required when moving a snapshot.")
            if not isinstance(self.move_to, str):
                raise ValueError("Expected --to-network to be a string.")
            if self.snapshot_uuid is None:
                raise ValueError("Snapshot UUID required.")


            # Move the snapshot to the specified network
            self.sdk.update_snapshot(
                uuid=self.snapshot_uuid,
                network_name=self.move_to
            )
            print(f"Snapshot {self.snapshot_uuid} moved to network {self.move_to}.")
            return
        elif self.subcommand == 'delete':
            # Delete the specified snapshot
            if self.snapshot_uuid is None:
                raise ValueError("Snapshot UUID required.")
            self.sdk.delete_snapshot(self.snapshot_uuid)
            print(f"Snapshot {self.snapshot_uuid} deleted.")
            return
        snapshots = self.sdk.list_snapshots(
            filter_net=self.network)
        snapshots = [asdict(snapshot, value_serializer=serialize) for snapshot in snapshots]
        if self.format == OutputFormat.JSON:
            print_json(data=snapshots, default=vars)
        elif self.format == OutputFormat.FAST_JSON:
            print(json.dumps(snapshots, default=vars))
        else:
            report_table = []
            skip_extras = ["errors_lines", "report_uuid", "additional_properties", "snapshot_uuid"]
            if self.network is not None:
                skip_extras.append("network_name")
            for row in snapshots:
                out = {k: v for k, v in row["snapshot"].items() if k not in ["organization_uuid", "network_uuid", "metadata", "additional_properties"]}
                out.update({k: v for k, v in row["extras"].items() if k not in skip_extras})
                report_table.append(out)
            display.print_frame(report_table, self.format)

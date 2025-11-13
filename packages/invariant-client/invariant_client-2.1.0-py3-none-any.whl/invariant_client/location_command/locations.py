import argparse
from invariant_client.bindings.invariant_instance_client.models.document_type import DocumentType
from invariant_client.bindings.invariant_instance_client.models.resource_type import ResourceType
from invariant_client.base_command.base_command import BaseCommand

class LocationsCommand(BaseCommand):
    use_argument_debug = True
    use_argument_group_format = True
    use_argument_format_tsv = True
    
    def __init__(self):
        super().__init__()
        self.network_name: str | None = None
        self.file_path: str | None = None
    
    @classmethod
    def parse_args(cls, subparsers: 'argparse._SubParsersAction[argparse.ArgumentParser]') -> None:
        command_locations = subparsers.add_parser(
            'locations',
            description='List or manage locations.',
            help='List or manage locations.'
        )
        cls._add_common_parser_arguments(command_locations)
        locations_subparsers = command_locations.add_subparsers(
            dest='locations_subcommand',
            required=True,
            help='Available subcommands for locations'
        )
        import_parser = locations_subparsers.add_parser(
            'import',
            description='Import locations from a file.',
            help='Import locations from a file.'
        )
        import_parser.add_argument(
            'network_name',
            help='The name of the network to import locations into.'
        )
        import_parser.add_argument(
            'file_path',
            help='Path to the file containing locations to import.'
        )
        cls._add_common_parser_arguments(import_parser)


    def set_config(self, args: 'argparse.Namespace', env: dict[str, str]) -> None:
        super().set_config(args, env)
        self.network_name = getattr(args, 'network_name', None)
        self.file_path = getattr(args, 'file_path', None)

    def execute(self) -> None:
        super().execute()
        self.sdk.import_editable_document(f"Network-Locations-{self.network_name}", DocumentType.INVARIANT_YAML_SPEC, ResourceType.LOCATIONS, self.file_path)
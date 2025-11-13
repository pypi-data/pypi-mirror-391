import argparse
from invariant_client.bindings.invariant_instance_client.models.document_type import DocumentType
from invariant_client.bindings.invariant_instance_client.models.resource_type import ResourceType
from invariant_client.base_command.base_command import BaseCommand

class DefinitionsCommand(BaseCommand):
    use_argument_debug = True
    use_argument_group_format = True
    use_argument_format_tsv = True
    
    def __init__(self):
        super().__init__()
        self.network_name: str | None = None
        self.file_path: str | None = None
    
    @classmethod
    def parse_args(cls, subparsers: 'argparse._SubParsersAction[argparse.ArgumentParser]') -> None:
        command_definitions = subparsers.add_parser(
            'definitions',
            description='List or manage definitions.',
            help='List or manage definitions.'
        )
        cls._add_common_parser_arguments(command_definitions)
        definitions_subparsers = command_definitions.add_subparsers(
            dest='definitions_subcommand',
            required=True,
            help='Available subcommands for definitions'
        )
        import_parser = definitions_subparsers.add_parser(
            'import',
            description='Import definitions from a file.',
            help='Import definitions from a file.'
        )
        import_parser.add_argument(
            'network_name',
            help='The name of the network to import definitions into.'
        )
        import_parser.add_argument(
            'file_path',
            help='Path to the file containing definitions to import.'
        )
        cls._add_common_parser_arguments(import_parser)


    def set_config(self, args: 'argparse.Namespace', env: dict[str, str]) -> None:
        super().set_config(args, env)
        self.network_name = getattr(args, 'network_name', None)
        self.file_path = getattr(args, 'file_path', None)

    def execute(self) -> None:
        super().execute()
        self.sdk.import_editable_document(f"Network-Definitions-{self.network_name}", DocumentType.INVARIANT_YAML_SPEC, ResourceType.DEFS, self.file_path)
import argparse
from invariant_client.bindings.invariant_instance_client.models.document_type import DocumentType
from invariant_client.bindings.invariant_instance_client.models.resource_type import ResourceType
from invariant_client.base_command.base_command import BaseCommand

class RulesCommand(BaseCommand):
    use_argument_debug = True
    use_argument_group_format = True
    use_argument_format_tsv = True
    
    def __init__(self):
        super().__init__()
        self.network_name: str | None = None
        self.file_path: str | None = None
    
    @classmethod
    def parse_args(cls, subparsers: 'argparse._SubParsersAction[argparse.ArgumentParser]') -> None:
        command_rules = subparsers.add_parser(
            'rules',
            description='List or manage rules.',
            help='List or manage rules.'
        )
        cls._add_common_parser_arguments(command_rules)
        rules_subparsers = command_rules.add_subparsers(
            dest='rules_subcommand',
            required=True,
            help='Available subcommands for rules'
        )
        import_parser = rules_subparsers.add_parser(
            'import',
            description='Import rules from a file.',
            help='Import rules from a file.'
        )
        import_parser.add_argument(
            'network_name',
            help='The name of the network to import rules into.'
        )
        import_parser.add_argument(
            'file_path',
            help='Path to the file containing rules to import.'
        )
        cls._add_common_parser_arguments(import_parser)


    def set_config(self, args: 'argparse.Namespace', env: dict[str, str]) -> None:
        super().set_config(args, env)
        self.network_name = getattr(args, 'network_name', None)
        self.file_path = getattr(args, 'file_path', None)

    def execute(self) -> None:
        super().execute()
        self.sdk.import_editable_document(f"Network-Rules-{self.network_name}", DocumentType.INVARIANT_YAML_SPEC, ResourceType.RULES, self.file_path)
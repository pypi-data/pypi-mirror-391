import argparse
import logging
import logging.config
import os
import sys
from typing import Type

from invariant_client.base_command.base_command import BaseCommand
from invariant_client.login_command.login import LoginCommand
from invariant_client.run_command.run import RunCommand
from invariant_client.fetch_command.fetch import FetchCommand
from invariant_client.sync_command.sync import SyncCommand
from invariant_client.show_command.show import ShowCommand
from invariant_client.snapshots_command.snapshots import SnapshotsCommand
from invariant_client.eval_command.eval import EvalCommand
from invariant_client.version_command.version import VersionCommand
from invariant_client.network_command.network import NetworkCommand
from invariant_client.rules_command.rules import RulesCommand
from invariant_client.definition_command.definitions import DefinitionsCommand
from invariant_client.location_command.locations import LocationsCommand


logger = logging.getLogger(__name__)


COMMANDS: dict[str, Type[BaseCommand]] = {
    'login': LoginCommand,
    'eval': EvalCommand,
    'run': RunCommand,
    'sync': SyncCommand,
    'fetch': FetchCommand,
    'show': ShowCommand,
    'snapshots': SnapshotsCommand,
    'networks': NetworkCommand,
    'version': VersionCommand,
    'rules': RulesCommand,
    'definitions': DefinitionsCommand,
    'locations': LocationsCommand,
}
LOGGER_NAME = "invariant"


def parse_args():
    parser = argparse.ArgumentParser(
        prog='invariant',
        description='Invariant analyzes network snapshots',
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(
        title='available commands',
        description='Run [command] --help for more information.',
        dest='command')

    for command_cls in COMMANDS.values():
        command_cls.parse_args(subparsers)

    parser.add_argument(
        '--version',
        dest='version',
        action='store_true',
        help="Display the client and server version.")

    args = parser.parse_args()

    command = getattr(args, 'command')
    if not command and not args.version:
        parser.print_help()
        exit(0)

    return args

class ModulePathFilter(logging.Filter):
    """
    A logging filter that drops records from a specific module path.
    """
    def __init__(self, block, name=""):
        super().__init__(name)
        self.block = block

    def filter(self, record):
        """
        Blocks a record if its pathname starts with the block and the level is WARNING or below.
        Returns False to block the record, True to allow it.
        """
        # Only filter if the log level is WARNING or below
        return not (
            record.levelno <= logging.WARNING and
            self.block and any(record.pathname.startswith(block_path) for block_path in self.block)
        )

def configure_logging(args):
    debug = getattr(args, 'debug', False)
    verbose = getattr(args, 'verbose', False)
    if debug:
        log_level = logging.DEBUG
    elif verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING
    handlers_config = {}
    formatters_config = {}
    try:
        import rich.console
        import rich.logging
        handlers_config["rich_handler"] = {
            "class": "rich.logging.RichHandler",
            "level": log_level,
            "rich_tracebacks": True,
            "omit_repeated_times": False,
            "tracebacks_show_locals": True,
            "tracebacks_suppress": [],
            "show_time": True,
            "show_path": False,
            "console": rich.console.Console(stderr=True)
        }
    except ImportError:
        formatters_config["custom_console_formatter"] = {
            "format": "%(asctime)s - %(name)s - %(levelname)-8s - %(module)s:%(lineno)d - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
        handlers_config["console_handler"] = {
            "class": "logging.StreamHandler",
            "level": log_level,  # Handler level
            "formatter": "custom_console_formatter", # Use the custom formatter
            "stream": "ext://sys.stderr"
        }

    dict_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": handlers_config,
        "root": {
            "level": log_level,
            "handlers": list(handlers_config.keys())
        },
        "formatters": formatters_config
    }
    logging.config.dictConfig(dict_config)

    if log_level >= logging.WARNING:
        # Override noisy modules:
        # - netconan: generates warnings when eliminating lines, which is debugging-relevant but not a true warning
        noisy_modules = []
        try:
            import netconan
            # This gives us the directory path of the 'netconan' library
            noisy_modules.append(os.path.dirname(netconan.__file__))

        except (ImportError, AttributeError) as e:
            pass

        if noisy_modules:
            noisy_filter = ModulePathFilter(block=noisy_modules)
            root_logger = logging.getLogger()
            for handler in root_logger.handlers:
                handler.addFilter(noisy_filter)


def EntryPoint():
    args = parse_args()
    configure_logging(args)
    
    try:
        EntryPoint_inner(args)
    except Exception as e:
        if getattr(args, 'debug', False):
            raise e
        print('Error: %s' % e, file=sys.stderr)
        exit(1)


def EntryPoint_inner(args):
    command = getattr(args, 'command')

    if getattr(args, 'version', False):
        command = 'version'

    if command not in COMMANDS:
        print(f"Unknown command {command}", file=sys.stderr)
        exit(1)
    command_inst = COMMANDS[command]()
    env = dict(os.environ)
    command_inst.set_config(args, env)
    command_inst.authenticate()
    command_inst.execute()

    # TODO add test-rule command:
    # Does NOT upload anything (just submits the rule)
    # Waits for the rule to be processed and displays some result info - possibly a table similar to 'run'
    # Question: should the CLI get into rule and network management? E.g. invariant network list, invariant network rules list, etc.

    # TODO now that non-blocking uploads are supported, consider making some changes:
    # 1. Wait for the latest snapshot to finish (same functionality as 'run'), e.g.
    #     print("Processing...")
    #     while datetime.datetime.now() < end_time:
    #         response = sdk.upload_is_running(exec_uuid)

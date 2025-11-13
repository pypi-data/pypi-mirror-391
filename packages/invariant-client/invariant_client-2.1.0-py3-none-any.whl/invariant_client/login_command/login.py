import datetime
import importlib
import logging
import ssl
import sys
import time
import typing

from msal_extensions import FilePersistence, build_encrypted_persistence
from xdg_base_dirs import xdg_data_home

from invariant_client import auth, pysdk
from invariant_client.base_command.base_command import CREDS_FILE_PATH, BaseCommand

if typing.TYPE_CHECKING:
    import argparse

logger = logging.getLogger(__name__)

class LoginCommand(BaseCommand):
    needs_authn = False
    use_argument_debug = True
    # No format options for this command

    @classmethod
    def parse_args(cls, subparsers: 'argparse._SubParsersAction[argparse.ArgumentParser]') -> None:
        command_login = subparsers.add_parser(
            'login',
            description='Authenticate by opening a link in your browser.',
            help="Authenticate by opening a link in your browser.")

        cls._add_common_parser_arguments(command_login)

    def set_config(self, args: 'argparse.Namespace', env: dict[str, str]) -> None:
        super().set_config(args, env)

    def execute(self):
        super().execute()
        # TODO warn before logging in if an API token is present (possibly check if it works?)
        workflow = auth.BrowserLoginFlow(self.invariant_domain, ssl.create_default_context())
        link = workflow.start()
        print("Open this link in your browser to log in:")
        print(link)
        creds = None
        try:
            end_time = datetime.datetime.now() + datetime.timedelta(minutes=3)
            # time.sleep(10)  # poor man's websocket
            time.sleep(6)  # poor man's websocket
            # TODO consider a nice animated "waiting" message for interactive terminal
            while not creds and end_time > datetime.datetime.now():
                result = workflow.poll_await_browser_creds()
                if isinstance(result, pysdk.AccessCredential):
                    creds = result
                    break
                elif isinstance(result, int):
                    time.sleep(result)
                else:
                    time.sleep(2)
            if not creds:
                print("Timed out.", file=sys.stderr)
                exit(1)

            cache_path = xdg_data_home().joinpath("invariantcli.token.cache")
            try:
                persistence = build_encrypted_persistence(str(cache_path))
                logger.debug(f'Using encrypted persistence {persistence.__class__.__name__}')
            except:
                logger.debug('Failed to build encrypted persistence, falling back to FilePersistence', exc_info=True)
                persistence = FilePersistence(cache_path)
            persistence.save(creds.to_json())

            sdk = pysdk.Invariant(
                creds=creds,
                settings=self.pysdk_settings,
                base_url=self.invariant_domain)
            status = sdk.status()

            client_version = ""
            try:
                client_version: str = importlib.resources.read_text("invariant_client", "VERSION", encoding='utf-8')
                client_version = client_version.strip()
            except:
                raise

            print(f"Logged in as {status.user.email} (client {client_version}) (tenant={creds.organization_name}).")
        except KeyboardInterrupt as e:
            print("Exiting...", file=sys.stderr)
            exit(1)

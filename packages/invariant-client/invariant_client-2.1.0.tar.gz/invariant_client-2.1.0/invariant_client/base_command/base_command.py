from abc import ABC, abstractmethod
import json
import pathlib
import sys
import typing

import httpx
from msal_extensions.persistence import PersistenceNotFound
from xdg_base_dirs import xdg_data_home

from invariant_client.pysdk import OutputFormat
from invariant_client import pysdk

if typing.TYPE_CHECKING:
    import argparse


CREDS_FILE_PATH = pathlib.Path.cwd()
try:
    CREDS_FILE_PATH = pathlib.Path.home()
except RuntimeError:
    pass
finally:
    CREDS_FILE_PATH = CREDS_FILE_PATH.joinpath('.invariant_creds')


class BaseCommand(ABC):
    needs_authn = True
    use_argument_debug = False
    use_argument_group_format = False
    use_argument_format_tsv = False
    use_argument_format_condensed = False

    httpx_client: httpx.Client | None = None
    """Test only - HTTPX client dependency."""

    @classmethod
    @abstractmethod
    def parse_args(cls, subparsers: 'argparse._SubParsersAction[argparse.ArgumentParser]') -> None:
        pass
 
    @classmethod
    def _add_common_parser_arguments(cls, parser: 'argparse.ArgumentParser'):
        parser.add_argument(
                '--verbose',
                dest='verbose',
                action='store_true',
                help='Enable verbose logging.',
            )
        if cls.use_argument_debug:
            parser.add_argument(
                '--debug',
                dest='debug',
                action='store_true',
                help='Enable detailed logging.',
            )

        if cls.use_argument_group_format:
            format_group = parser.add_mutually_exclusive_group()
            format_group.add_argument(
                '--json',
                dest='json',
                action='store_true',
                help='Output data as JSON.',
            )
            format_group.add_argument(
                '--fast-json',
                dest='fast_json',
                action='store_true',
                help='Output data as JSON (unformatted).',
            )

            if cls.use_argument_format_tsv:
                format_group.add_argument(
                    '--tsv',
                    dest='tsv',
                    action='store_true',
                    help='Output data as TSV.',
                )

            if cls.use_argument_format_condensed:
                format_group.add_argument(
                    '--condensed',
                    dest='condensed',
                    action='store_true',
                    help='Output only snapshot ID and outcome.',
                )

    @abstractmethod
    def set_config(self, args: 'argparse.Namespace', env: dict[str, str]) -> None:
        self.env = env
        self.invariant_domain = self.get_invariant_domain(env)

        self.format = OutputFormat.TABULATE
        if getattr(args, 'json', False):
            self.format = OutputFormat.JSON
        elif getattr(args, 'fast_json', False):
            self.format = OutputFormat.FAST_JSON
        elif getattr(args, 'tsv', False):
            self.format = OutputFormat.TSV
        elif getattr(args, 'condensed', False):
            self.format = OutputFormat.CONDENSED
        
        self.debug = getattr(args, 'debug', False)

        self.pysdk_settings: pysdk.Settings = {
            'format': self.format,
            'debug': self.debug,
        }

    def get_invariant_domain(self, env: dict[str, str]) -> str:
        return env.get('INVARIANT_DOMAIN', 'https://prod.invariant.tech')

    def authenticate(self) -> None:
        if not self.needs_authn:
            return

        # Load credentials or error
        def get_creds() -> pysdk.AccessCredential | None:
            creds = pysdk.AccessCredential.from_env(
                self.env,
                base_url=self.invariant_domain,
                httpx_client=self.httpx_client)
            if creds:
                return creds

            try:
                cache_path = xdg_data_home().joinpath("invariantcli.token.cache")
                creds = pysdk.AccessCredential.from_msal(
                    cache_path,
                    base_url=self.invariant_domain,
                    httpx_client=self.httpx_client)
                if creds:
                    return creds
            except PersistenceNotFound:
                creds = None
            except FileNotFoundError:
                creds = None

            try:
                creds = pysdk.AccessCredential.from_file(
                    CREDS_FILE_PATH,
                    base_url=self.invariant_domain,
                    httpx_client=self.httpx_client)
                if creds:
                    return creds
            except FileNotFoundError:
                # Expected
                creds = None

        try:
            creds = get_creds()
            if not creds:
                print("Please run 'invariant login' to authenticate.", file=sys.stderr)
                exit(1)

        except pysdk.AuthorizationException as e:
            print(f"Error: {e}", file=sys.stderr)
            print("Please run 'invariant login' to authenticate.", file=sys.stderr)
            if self.debug:
                raise e
            exit(1)
        except pysdk.RemoteError as e:
            print(f"Error: {e}", file=sys.stderr)
            if self.debug:
                raise e
            exit(1)

        settings = self.pysdk_settings
        self.sdk = pysdk.Invariant(
            creds=creds,
            settings=settings,
            base_url=self.invariant_domain,
            httpx_client=self.httpx_client)


    @abstractmethod
    def execute(self) -> None:
        pass
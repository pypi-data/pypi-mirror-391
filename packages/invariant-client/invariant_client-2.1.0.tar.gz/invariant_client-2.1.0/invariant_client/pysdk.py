from dataclasses import dataclass
import enum
import io
import json
import logging
import pathlib
import ssl
import tempfile
from typing import IO, BinaryIO, Optional, TypeAlias, TypedDict, Union
import typing
import urllib.parse as urllib_parse
import uuid
import httpx
import pandas

from msal_extensions import FilePersistence, build_encrypted_persistence
import pyarrow.feather as feather

from invariant_client import pysdk
from invariant_client.bindings.invariant_instance_client.models.email_subscriber import EmailSubscriber
from invariant_client.bindings.invariant_instance_client.models.slack_subscriber import SlackSubscriber
from invariant_client.lib import fetcher
from invariant_client.bindings.invariant_instance_client.api.organization.ui_status_organization_name_api_v_1_ui_get import sync_detailed as ui_status_organization_name_api_v_1_ui_get

from invariant_client.bindings.invariant_instance_client.client import AuthenticatedClient as InstanceAuthenticatedClient
from invariant_client.bindings.invariant_instance_client import models
from invariant_client.bindings.invariant_instance_client import types
from invariant_client.bindings.invariant_instance_client.api.organization.list_reports_organization_name_api_v_1_reports_get import sync_detailed as list_reports_organization_name_api_v_1_reports_get
from invariant_client.bindings.invariant_instance_client.api.organization.refresh_organization_name_api_v1_refresh_post import sync_detailed as refresh_organization_name_api_v1_refresh_post
from invariant_client.bindings.invariant_instance_client.models.file_index import FileIndex
from invariant_client.bindings.invariant_instance_client.models.report_text_summary_request import ReportTextSummaryRequest
from invariant_client.bindings.invariant_login_client.client import AuthenticatedClient as LoginAuthenticatedClient, Client as LoginClient
from invariant_client.bindings.invariant_instance_client.api.organization.create_network_organization_name_api_v_1_networks_post import sync_detailed as create_network_organization_name_api_v_1_networks_post
from invariant_client.bindings.invariant_instance_client.api.organization.delete_network_organization_name_api_v_1_networks_network_uuid_delete import sync_detailed as delete_network_organization_name_api_v_1_networks_network_uuid_delete
from invariant_client.bindings.invariant_instance_client.api.organization.upload_snapshot_organization_name_api_v_1_uploadsnapshot_post import sync_detailed as upload_snapshot_organization_name_api_v_1_uploadsnapshot_post
from invariant_client.bindings.invariant_instance_client.api.organization.upload_snapshot_status_organization_name_api_v_1_uploadsnapshot_status_get import sync_detailed as upload_snapshot_status_organization_name_api_v_1_uploadsnapshot_status_get
from invariant_client.bindings.invariant_instance_client.api.organization.get_report_summary_organization_name_api_v_1_reports_report_id_summary_get import sync_detailed as get_report_summary_organization_name_api_v_1_reports_report_id_summary_get
from invariant_client.bindings.invariant_instance_client.api.organization.get_report_summary_text_summary_organization_name_api_v_1_reports_report_id_summary_text_get import sync_detailed as get_report_summary_text_summary_organization_name_api_v_1_reports_report_id_summary_text_get
from invariant_client.bindings.invariant_instance_client.api.organization.get_report_organization_name_api_v_1_reports_report_id_get import _get_kwargs as get_report_organization_name_api_v_1_reports_report_id_get__get_kwargs
from invariant_client.bindings.invariant_instance_client.api.organization.get_report_text_summary_organization_name_api_v_1_reports_report_id_text_get import sync_detailed as get_report_text_summary_organization_name_api_v_1_reports_report_id_text_get
from invariant_client.bindings.invariant_instance_client.api.organization.list_snapshots_organization_name_api_v_1_snapshots_get import sync_detailed as list_snapshots_organization_name_api_v_1_snapshots_get
from invariant_client.bindings.invariant_instance_client.api.organization.list_networks_organization_name_api_v_1_networks_get import sync_detailed as list_networks_organization_name_api_v_1_networks_get
from invariant_client.bindings.invariant_instance_client.api.organization.update_snapshot_organization_name_api_v_1_snapshots_snapshot_uuid_post import sync_detailed as update_snapshot_organization_name_api_v_1_snapshots_snapshot_uuid_post
from invariant_client.bindings.invariant_instance_client.api.organization.modify_network_organization_name_api_v_1_networks_network_uuid_post import sync_detailed as modify_network_organization_name_api_v_1_networks_network_uuid_post
from invariant_client.bindings.invariant_instance_client.api.organization.delete_snapshot_organization_name_api_v_1_snapshots_snapshot_uuid_delete import sync_detailed as delete_snapshot_organization_name_api_v_1_snapshots_snapshot_uuid_delete
from invariant_client.bindings.invariant_instance_client.api.organization.try_rule_ll_organization_name_api_v_1_snapshots_snapshot_uuid_try_rule_post import sync_detailed as try_rule_ll_organization_name_api_v_1_snapshots_snapshot_uuid_try_rule_post
from invariant_client.bindings.invariant_instance_client.api.organization.list_monitor_targets_organization_name_api_v_1_monitor_targets_get import sync_detailed as list_monitor_targets_organization_name_api_v_1_monitor_targets_get
from invariant_client.bindings.invariant_instance_client.api.organization.create_monitor_targets_organization_name_api_v_1_monitor_targets_post import sync_detailed as create_monitor_targets_organization_name_api_v_1_monitor_targets_post
from invariant_client.bindings.invariant_instance_client.api.organization.delete_monitor_target_organization_name_api_v_1_monitor_targets_monitor_target_uuid_delete import sync_detailed as delete_monitor_target_organization_name_api_v_1_monitor_targets_monitor_target_uuid_delete
from invariant_client.bindings.invariant_instance_client.api.organization.list_notification_groups_organization_name_api_v_1_notification_groups_get import sync_detailed as list_notification_groups_organization_name_api_v_1_notification_groups_get
from invariant_client.bindings.invariant_instance_client.api.organization.create_notification_group_organization_name_api_v_1_notification_groups_post import sync_detailed as create_notification_group_organization_name_api_v_1_notification_groups_post
from invariant_client.bindings.invariant_instance_client.api.organization.delete_notification_group_organization_name_api_v_1_notification_groups_notification_group_uuid_delete import sync_detailed as delete_notification_group_organization_name_api_v_1_notification_groups_notification_group_uuid_delete
from invariant_client.bindings.invariant_instance_client.api.organization.import_editable_document_organization_name_api_v_1_edoc_import_post import sync_detailed as import_editable_document_organization_name_api_v_1_edoc_import_post
from invariant_client.bindings.invariant_login_client.api.login.get_instances_api_v1_login_get_instances_post import sync_detailed as get_instances_api_v1_login_get_instances_post
from invariant_client.bindings.invariant_login_client.models.base_error_response import BaseErrorResponse
from invariant_client.bindings.invariant_login_client.models.validation_error_response import ValidationErrorResponse


logger = logging.getLogger(__name__)


DOMAIN_NAME = "https://prod.invariant.tech"


class NoOrganization(Exception):
    """Credentials must be paired with an organization name."""


ErrorResponseType: TypeAlias = BaseErrorResponse | ValidationErrorResponse


class RemoteError(Exception):
    """Generic server-side or connection error."""


class AuthorizationException(Exception):
    """Server authentication rejected."""


class OutputFormat(enum.Enum):
    TABULATE = enum.auto()
    JSON = enum.auto()
    TSV = enum.auto()
    FAST_JSON = enum.auto()
    CONDENSED = enum.auto()


class Settings(TypedDict):
    format: OutputFormat
    debug: bool


@dataclass
class AccessCredential:
    """An invariant access credential."""

    access_token: Optional[str]
    refresh_token: Optional[str]
    organization_name: str

    INVARIANT_ACCESS_TOKEN = 'INVARIANT_ACCESS_TOKEN'
    INVARIANT_API_TOKEN = 'INVARIANT_API_TOKEN'
    INVARIANT_API_TOKEN_PATH = 'INVARIANT_API_TOKEN_PATH'
    INVARIANT_ORGANIZATION_NAME = 'INVARIANT_ORGANIZATION_NAME'

    @classmethod
    def from_env(
        cls,
        env_data: dict[str, str],
        base_url: Optional[str] = None,
        verify_ssl: Optional[str | bool | ssl.SSLContext] = None,
        httpx_client: Optional[httpx.Client] = None,
        **kwargs,
    ) -> Optional['AccessCredential']:
        access_token = env_data.get(cls.INVARIANT_ACCESS_TOKEN)
        refresh_token = env_data.get(cls.INVARIANT_API_TOKEN)
        if not refresh_token:
            api_token_path = env_data.get(cls.INVARIANT_API_TOKEN_PATH)
            if api_token_path:
                with open(api_token_path, 'r') as f:
                    refresh_token = f.read().strip()
        organization_name = env_data.get(cls.INVARIANT_ORGANIZATION_NAME)
        return cls.build(organization_name, access_token, refresh_token, base_url=base_url, verify_ssl=verify_ssl, httpx_client=httpx_client, **kwargs)

    @classmethod
    def from_file(
        cls,
        file_path: 'typing.Union[pathlib.Path, str]',
        base_url: Optional[str] = None,
        verify_ssl: Optional[str | bool | ssl.SSLContext] = None,
        httpx_client: Optional[httpx.Client] = None,
        **kwargs
    ) -> Optional['AccessCredential']:
        with open(file_path, "r") as f:
            data: dict = json.load(f)
        access_token = data.get(cls.INVARIANT_ACCESS_TOKEN)
        refresh_token = data.get(cls.INVARIANT_API_TOKEN)
        organization_name = data.get(cls.INVARIANT_ORGANIZATION_NAME)
        return cls.build(organization_name, access_token, refresh_token, base_url=base_url, verify_ssl=verify_ssl, httpx_client=httpx_client, **kwargs)

    @classmethod
    def from_msal(
        cls,
        cache_path: 'typing.Union[pathlib.Path, str]',
        base_url: Optional[str] = None,
        verify_ssl: Optional[str | bool | ssl.SSLContext] = None,
        httpx_client: Optional[httpx.Client] = None,
        **kwargs
    ) -> Optional['AccessCredential']:
        try:
            persistence = build_encrypted_persistence(str(cache_path))
            logger.debug(f'Using encrypted persistence {persistence.__class__.__name__}')
        except:
            logger.debug('Failed to build encrypted persistence, falling back to FilePersistence', exc_info=True)
            persistence = FilePersistence(cache_path)
        data = persistence.load()
        data: dict = json.loads(data)
        access_token = data.get(cls.INVARIANT_ACCESS_TOKEN)
        refresh_token = data.get(cls.INVARIANT_API_TOKEN)
        organization_name = data.get(cls.INVARIANT_ORGANIZATION_NAME)
        return cls.build(organization_name, access_token, refresh_token, base_url=base_url, verify_ssl=verify_ssl, httpx_client=httpx_client, **kwargs)

    @classmethod
    def build(
        cls,
        organization_name: str | None,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        base_url: Optional[str] = None,
        verify_ssl: Optional[str | bool | ssl.SSLContext] = None,
        httpx_client: Optional[httpx.Client] = None,
        **kwargs
    ):
        # if access_token, try it (get ui? org?)
        # - if error and no RT, error to user
        # if refresh_token, but no organization_name, error to user
        # if refresh_token, try it, and error to user if error
        # otherwise just return None
        if not (organization_name or access_token or refresh_token):
            return None

        error: Exception | None = None
        verify_ssl = verify_ssl or ssl.create_default_context()
        if not organization_name:
            raise NoOrganization("INVARIANT_ORGANIZATION_NAME must be given.")
        if access_token:
            creds = cls(access_token=access_token, refresh_token=None, organization_name=organization_name)
            client = pysdk.Invariant(creds=creds, settings={}, base_url=base_url, verify_ssl=verify_ssl, httpx_client=httpx_client, **kwargs)
            try:
                client.status() # Will throw if access token is no good
                return creds
            except RemoteError as r_error:
                error = r_error
            # try it
            # try to set organization_name
            # if error and no RT, error to user
            # if error and RT, pass thru to RT
        if refresh_token:
            creds = cls(refresh_token=refresh_token, organization_name=organization_name, access_token=None)
            base_url = base_url or DOMAIN_NAME
            client = pysdk.InvariantLogin(settings={}, creds=creds, base_url=base_url, verify_ssl=verify_ssl, httpx_client=httpx_client, **kwargs)
            try:
                sdk = client.to_instance_sdk(verify_ssl, **kwargs)
                return sdk.creds
            except RemoteError as r_error:
                error = r_error

        if error is not None:
            raise error

    def to_json(self) -> str:
        data = {}
        if self.access_token:
            data[AccessCredential.INVARIANT_ACCESS_TOKEN] = self.access_token
        if self.refresh_token:
            data[AccessCredential.INVARIANT_API_TOKEN] = self.refresh_token
        if self.organization_name:
            data[AccessCredential.INVARIANT_ORGANIZATION_NAME] = self.organization_name
        return json.dumps(data)



class Invariant:

    client: InstanceAuthenticatedClient
    creds: AccessCredential
    base_url: str

    def __init__(
            self,
            creds: AccessCredential,
            settings: dict,
            base_url: Optional[str] = None,
            verify_ssl: Optional[str | bool | ssl.SSLContext] = None,
            httpx_client: Optional[httpx.Client] = None,
            **kwargs):
        self.creds = creds
        self.settings = settings
        base_url = base_url or DOMAIN_NAME
        self.base_url = self.app_base_url(base_url)

        # Prefer to use the Python default SSL context over the HTTPX SSL context, which does not consider system trust roots
        # Users can revert to the HTTPX SSL context with 'verify_ssl=True'
        verify_ssl = verify_ssl or ssl.create_default_context()
        self.client = InstanceAuthenticatedClient(
            self.base_url,
            token=creds.access_token,
            verify_ssl=verify_ssl,
            **kwargs)
        if httpx_client is not None:
            httpx_client.headers[self.client.auth_header_name] = (
                f"{self.client.prefix} {self.client.token}" if self.client.prefix else self.client.token
            )
            self.client.set_httpx_client(httpx_client)
    
    @staticmethod
    def app_base_url(base_domain_name: str) -> str:
        url = urllib_parse.urlparse(base_domain_name)
        url = url._replace(netloc=f'app.{url.netloc}')
        return url.geturl()
    
    def upload_snapshot(
            self,
            source: 'Union[IO, BinaryIO]',
            network: Optional[str] = None,
            role: Optional[str] = None,
            compare_to: Optional[str] = None) -> models.UploadSnapshotResponse:
        """Zip and upload the current folder. Display a summary of processing results when complete."""
        response = upload_snapshot_organization_name_api_v_1_uploadsnapshot_post(
            self.creds.organization_name,
            client=self.client,
            body=models.BodyUploadSnapshotOrganizationNameApiV1UploadsnapshotPost(
                file=types.File(
                    payload=source,
                    file_name="snapshot_upload.zip",
                    mime_type="application/zip"
                )
            ),
            network=network,
            role=role)
        response = response.parsed
        # TODO idiom should be to examine error responses by status code as we do in the UI
        # Note that DNS NX_DOMAIN error actually raises httpx.ConnectError (-2: Name or service not known) at request time
        # Connection refused also raises httpx.ConnectError (111: Connection refused)
        if not response:
            raise RemoteError(f"Unable to connect to {self.base_url}")
        if isinstance(response, models.ChallengeResponse):
            raise AuthorizationException(f"{response.title}: {response.detail}")
        if not isinstance(response, models.UploadSnapshotResponse):
            raise RemoteError(response)
        return response
    
    def upload_is_running(self, uuid: str) -> models.UploadSnapshotStatusResponse:
        response = upload_snapshot_status_organization_name_api_v_1_uploadsnapshot_status_get(
            self.creds.organization_name,
            client=self.client,
            uuid=uuid,
        )
        response = response.parsed
        if not response:
            raise RemoteError(f"Unable to connect to {self.base_url}")
        if isinstance(response, models.ChallengeResponse):
            raise AuthorizationException(f"{response.title}: {response.detail}")
        if not isinstance(response, models.UploadSnapshotStatusResponse):
            raise RemoteError(response)
        return response

    def list_snapshots(
            self,
            filter_net: str | None = None,
            filter_session: bool | None= None,
            limit: int | None = None) -> list[models.ListSnapshotsResponse]:
        kwargs = {}
        if filter_session:
            kwargs['filter_session'] = 1
        if filter_net:
            kwargs['network_name'] = filter_net
        if limit:
            kwargs['limit'] = limit
        response = list_snapshots_organization_name_api_v_1_snapshots_get(
            self.creds.organization_name,
            client=self.client,
            **kwargs)
        response = response.parsed
        if response is None:
            raise RemoteError(f"Unable to connect to {self.base_url}")
        if isinstance(response, models.ChallengeResponse):
            raise AuthorizationException(f"{response.title}: {response.detail}")
        if isinstance(response, models.BaseErrorResponse) or isinstance(response, models.ValidationErrorResponse):
            raise RemoteError(response)
        return response

    def update_snapshot(
            self,
            uuid: uuid.UUID,
            network_name: str):
        response = update_snapshot_organization_name_api_v_1_snapshots_snapshot_uuid_post(
            self.creds.organization_name,
            snapshot_uuid=uuid,
            body=models.UpdateSnapshotsRequest(
                network_name=network_name,
            ),
            client=self.client
        )
        response = response.parsed
        if response is None:
            raise RemoteError(f"Unable to connect to {self.base_url}")
        if isinstance(response, models.ChallengeResponse):
            raise AuthorizationException(f"{response.title}: {response.detail}")
        if isinstance(response, models.BaseErrorResponse) or isinstance(response, models.ValidationErrorResponse):
            raise RemoteError(response)
        return response

    def delete_snapshot(
            self,
            uuid: uuid.UUID):
        response = delete_snapshot_organization_name_api_v_1_snapshots_snapshot_uuid_delete(
            self.creds.organization_name,
            snapshot_uuid=uuid,
            client=self.client
        )
        response = response.parsed
        if isinstance(response, models.ChallengeResponse):
            raise AuthorizationException(f"{response.title}: {response.detail}")
        if isinstance(response, models.BaseErrorResponse) or isinstance(response, models.ValidationErrorResponse):
            raise RemoteError(response)
        return response

    def list_networks(
            self,
            limit: int | None = None) -> models.ListNetworksResponse:
        kwargs = {}
        if limit:
            kwargs['limit'] = limit
        response = list_networks_organization_name_api_v_1_networks_get(
            self.creds.organization_name,
            client=self.client,
            **kwargs)
        response = response.parsed
        if response is None:
            raise RemoteError(f"Unable to connect to {self.base_url}")
        if isinstance(response, models.ChallengeResponse):
            raise AuthorizationException(f"{response.title}: {response.detail}")
        if isinstance(response, models.BaseErrorResponse) or isinstance(response, models.ValidationErrorResponse):
            raise RemoteError(response)
        return response


    def create_network(
            self,
            name: str,
            comment: Optional[str] = None):
        if comment is None:
            comment = ""
        response = create_network_organization_name_api_v_1_networks_post(
            self.creds.organization_name,
            client=self.client,
            body=models.CreateNetworkRequest(
                name=name,
                comment=comment,
            ))
        response = response.parsed
        if isinstance(response, models.ChallengeResponse):
            raise AuthorizationException(f"{response.title}: {response.detail}")
        if isinstance(response, models.BaseErrorResponse) or isinstance(response, models.ValidationErrorResponse):
            raise RemoteError(response)
        return response

    def rename_network_by_name(self, network_name: str, new_name: str):
        """Renames a network and updates references via the API."""
        networks = self.list_networks()
        network_uuid = None
        for network in networks.networks:
            if network.name == network_name:
                network_uuid = network.uuid
                break
        if not network_uuid:
            raise RemoteError(f"Network '{network_name}' not found.")
        return self.rename_network(network_uuid, new_name)

    def rename_network(self, network_uuid: uuid.UUID, new_name: str):
        """Renames a network and updates references via the API."""
        response = modify_network_organization_name_api_v_1_networks_network_uuid_post(
            self.creds.organization_name,
            network_uuid,
            client=self.client,
            body=models.ModifyNetworkRequest(name=new_name, comment=None)
        )
        response = response.parsed
        if isinstance(response, models.ChallengeResponse):
            raise AuthorizationException(f"{response.title}: {response.detail}")
        if isinstance(response, models.BaseErrorResponse) or isinstance(response, models.ValidationErrorResponse):
            raise RemoteError(response)

        return response

    def delete_network(self, network_uuid: uuid.UUID):
        response = delete_network_organization_name_api_v_1_networks_network_uuid_delete(
            organization_name=self.creds.organization_name,
            network_uuid=network_uuid,
            client=self.client
        )
        response = response.parsed
        if isinstance(response, models.ChallengeResponse):
            raise AuthorizationException(f"{response.title}: {response.detail}")
        if isinstance(response, models.BaseErrorResponse) or isinstance(response, models.ValidationErrorResponse):
            raise RemoteError(response)
        return response

    def list_reports(
            self,
            filter_session: bool | None = None,
            filter_net: str | None = None,
            filter_role: str | None = None,
            limit: int | None = None) -> models.ListReportsResponse:
        kwargs = {}
        if filter_session:
            kwargs['filter_session'] = 1
        if filter_net:
            kwargs['filter_net'] = filter_net
        if filter_role:
            kwargs['filter_role'] = filter_role
        if limit:
            kwargs['limit'] = limit
        response = list_reports_organization_name_api_v_1_reports_get(
            self.creds.organization_name,
            client=self.client,
            **kwargs)
        response = response.parsed
        if response is None:
            raise RemoteError(f"Unable to connect to {self.base_url}")
        if isinstance(response, models.ChallengeResponse):
            raise AuthorizationException(f"{response.title}: {response.detail}")
        if not isinstance(response, models.ListReportsResponse):
            raise RemoteError(response)
        return response

    def report_detail(
            self,
            report_uuid: str) -> models.GetReportSummaryResponse:
        response = get_report_summary_organization_name_api_v_1_reports_report_id_summary_get(self.creds.organization_name, report_uuid, client=self.client)
        response = response.parsed
        if not response:
            raise RemoteError(f"Unable to connect to {self.base_url}")
        if isinstance(response, models.ChallengeResponse):
            raise AuthorizationException(f"{response.title}: {response.detail}")
        if not isinstance(response, models.GetReportSummaryResponse):
            raise RemoteError(response)
        return response

    def report_detail_text(
            self,
            report_uuid: str,
            json_mode: bool
        ) -> models.ReportTextSummaryResponse:
        body = ReportTextSummaryRequest(
            traces=False,
            mode='json' if json_mode else 'text')
        response = get_report_summary_text_summary_organization_name_api_v_1_reports_report_id_summary_text_get(
            self.creds.organization_name,
            report_uuid,
            client=self.client,
            body=body)
        response = response.parsed
        if not response:
            raise RemoteError(f"Unable to connect to {self.base_url}")
        if isinstance(response, models.ChallengeResponse):
            raise AuthorizationException(f"{response.title}: {response.detail}")
        if not isinstance(response, models.ReportTextSummaryResponse):
            raise RemoteError(response)
        return response

    def snapshot_file(
            self,
            file_locator: FileIndex | uuid.UUID) -> pandas.DataFrame:
        """Download a remote file as a pandas DataFrame."""
        if isinstance(file_locator, uuid.UUID):
            file_uuids = [file_locator]
        elif isinstance(file_locator, FileIndex):
            file_uuids = file_locator.all_files
        else:
            raise ValueError('Unsupported file locator format. You may a newer client version.')

        responses: list[pandas.DataFrame] = []
        for file_uuid in file_uuids:
            kwargs = get_report_organization_name_api_v_1_reports_report_id_get__get_kwargs(
                organization_name=self.creds.organization_name,
                report_id=file_uuid,
            )
            response = self.client.get_httpx_client().request(
                **kwargs,
            )

            # TODO approach checking for errors more carefully as the expected value is not JSON
            if not response:
                raise RemoteError(f"Unable to connect to {self.base_url}")
            # if isinstance(response, models.ChallengeResponse):
            #     raise AuthorizationException(f"{response.title}: {response.detail}")
            # if isinstance(response, models.BaseErrorResponse):
            #     raise RemoteError(response)
            file_df = feather.read_feather(io.BytesIO(response.content))
            responses.append(file_df)
        combined_df = pandas.concat(responses)
        return combined_df

    def try_rule(
            self,
            snapshot_uuid: uuid.UUID,
            rule: str,  # YAML access policy file containing a single rule
            locations: str,  # Base64-encoded string (zip file)
            defs: str,  # Base64-encoded string (zip file)
    ) -> models.ExecResponse:
        """Zip and upload the current folder. Display a summary of processing results when complete."""
        body = models.TryRuleRequest(
            rule=rule,
            locations=locations,
            defs=defs)
        response = try_rule_ll_organization_name_api_v_1_snapshots_snapshot_uuid_try_rule_post(
            self.creds.organization_name,
            snapshot_uuid=snapshot_uuid,
            client=self.client,
            body=body)
        response = response.parsed
        # TODO idiom should be to examine error responses by status code as we do in the UI
        # Note that DNS NX_DOMAIN error actually raises httpx.ConnectError (-2: Name or service not known) at request time
        # Connection refused also raises httpx.ConnectError (111: Connection refused)
        if not response:
            raise RemoteError(f"Unable to connect to {self.base_url}")
        if isinstance(response, models.ChallengeResponse):
            raise AuthorizationException(f"{response.title}: {response.detail}")
        if not isinstance(response, models.ExecResponse):
            raise RemoteError(response)
        return response

    def show(
            self,
            snapshot: str,
            file: str):
        pass

    def show_solution(
            self,
            snapshot: str,
            solution: str):
        pass

    def status(self) -> models.UIStatusResponse:
        if not self.creds or not self.creds.access_token:
            raise ValueError("status requires an access token.")
        response = ui_status_organization_name_api_v_1_ui_get(self.creds.organization_name, client=self.client)
        response = response.parsed
        if not response:
            raise RemoteError(f"Unable to connect to {self.base_url}")
        if isinstance(response, models.ChallengeResponse):
            raise AuthorizationException(f"{response.title}: {response.detail}")
        if not isinstance(response, models.UIStatusResponse):
            raise RemoteError(response)
        return response

    def list_monitor_targets(self) -> list[models.MonitorTarget]:
        response = list_monitor_targets_organization_name_api_v_1_monitor_targets_get(
            self.creds.organization_name,
            client=self.client
        )
        response = response.parsed
        if response is None:
            raise RemoteError(f"Unable to connect to {self.base_url}")
        if isinstance(response, models.ChallengeResponse):
            raise AuthorizationException(f"{response.title}: {response.detail}")
        if isinstance(response, models.BaseErrorResponse) or isinstance(response, models.ValidationErrorResponse):
            raise RemoteError(response)
        return response

    def create_monitor_target(self, name: str, comment: str, repository_url: str, monitor_path: str, network_name: str):
        response = create_monitor_targets_organization_name_api_v_1_monitor_targets_post(
            self.creds.organization_name,
            client=self.client,
            body=models.CreateMonitorTargetRequest(
                name=name,
                comment=comment,
                repository_url=repository_url,
                monitor_path=monitor_path,
                network_name=network_name
            )
        )
        response = response.parsed
        if isinstance(response, models.ChallengeResponse):
            raise AuthorizationException(f"{response.title}: {response.detail}")
        if isinstance(response, models.BaseErrorResponse) or isinstance(response, models.ValidationErrorResponse):
            raise RemoteError(response)
        return response

    def delete_monitor_target(self, monitor_target_uuid: uuid.UUID):
        response = delete_monitor_target_organization_name_api_v_1_monitor_targets_monitor_target_uuid_delete(
            self.creds.organization_name,
            monitor_target_uuid=monitor_target_uuid,
            client=self.client
        )
        response = response.parsed
        if isinstance(response, models.ChallengeResponse):
            raise AuthorizationException(f"{response.title}: {response.detail}")
        if isinstance(response, models.BaseErrorResponse) or isinstance(response, models.ValidationErrorResponse):
            raise RemoteError(response)
        return response

    def list_notification_groups(self) -> models.ListNotificationGroupsResponse:
        response = list_notification_groups_organization_name_api_v_1_notification_groups_get(
            self.creds.organization_name,
            client=self.client
        )
        response = response.parsed
        if response is None:
            raise RemoteError(f"Unable to connect to {self.base_url}")
        if isinstance(response, models.ChallengeResponse):
            raise AuthorizationException(f"{response.title}: {response.detail}")
        if isinstance(response, models.BaseErrorResponse) or isinstance(response, models.ValidationErrorResponse):
            raise RemoteError(response)
        return response

    def create_notification_group(self, name: str, comment: str, subscribers: Optional[list[EmailSubscriber | SlackSubscriber]] = None, network_subscriptions: Optional[list[str]] = None):
        if subscribers is None:
            subscribers = []
        if network_subscriptions is None:
            network_subscriptions = []
        response = create_notification_group_organization_name_api_v_1_notification_groups_post(
            self.creds.organization_name,
            client=self.client,
            body=models.CreateNotificationGroupRequest(
                name=name,
                comment=comment,
                subscribers=subscribers,
                network_subscriptions=network_subscriptions
            )
        )
        response = response.parsed
        if isinstance(response, models.ChallengeResponse):
            raise AuthorizationException(f"{response.title}: {response.detail}")
        if isinstance(response, models.BaseErrorResponse) or isinstance(response, models.ValidationErrorResponse):
            raise RemoteError(response)
        return response

    def delete_notification_group(self, notification_group_uuid: uuid.UUID):
        response = delete_notification_group_organization_name_api_v_1_notification_groups_notification_group_uuid_delete(
            self.creds.organization_name,
            notification_group_uuid=notification_group_uuid,
            client=self.client
        )
        response = response.parsed
        if isinstance(response, models.ChallengeResponse):
            raise AuthorizationException(f"{response.title}: {response.detail}")
        if isinstance(response, models.BaseErrorResponse) or isinstance(response, models.ValidationErrorResponse):
            raise RemoteError(response)
        return response

    def fetch(self, config_path, output_path):
        config_fetcher = fetcher.Fetcher(config_path, output_path)
        config_fetcher.fetch()
    
    def import_editable_document(self, network_name: str, document_type: str, resource_type: str, file_path: str):
        """
        Import an editable document into the system.

        Args:
            document_type (str): The type of the document to import.
            resource_type (str): The resource type associated with the document.
            file_path (str): The path to the file to be imported.

        Returns:
            models.EditableDocumentResult: The result of the import operation.
        """
        with open(file_path, "rb") as file:
            
            body = models.BodyImportEditableDocumentOrganizationNameApiV1EdocImportPost(
                # document_type=document_type,
                # resource_type=resource_type,
                file=types.File(
                    payload=file,
                    file_name=pathlib.Path(file_path).name,
                    mime_type="application/octet-stream"
                )
            )
            
            response = import_editable_document_organization_name_api_v_1_edoc_import_post(
                self.creds.organization_name,
                client=self.client,
                body=body,
                file_path=file_path,
                resource_set_name=network_name,
                document_type=document_type,
                resource_type=resource_type
            )
            response = response.parsed
            if isinstance(response, models.ChallengeResponse):
                raise AuthorizationException(f"{response.title}: {response.detail}")
            if isinstance(response, models.BaseErrorResponse) or isinstance(response, models.ValidationErrorResponse):
                raise RemoteError(response)
            return response


class InvariantLogin:

    client: LoginClient
    login_client: LoginAuthenticatedClient | LoginClient
    creds: AccessCredential
    login_creds: AccessCredential
    base_url: str

    def __init__(
            self,
            settings: dict,
            creds: Optional[AccessCredential] = None,
            login_session_creds: Optional[AccessCredential] = None,
            base_url: Optional[str] = None,
            verify_ssl: Optional[str | bool | ssl.SSLContext] = None,
            httpx_client: Optional[httpx.Client] = None,
            **kwargs):
        self.creds = creds
        self.login_creds = login_session_creds
        self.settings = settings
        self.base_url = base_url or DOMAIN_NAME
        self.httpx_client = httpx_client

        # Prefer to use the Python default SSL context over the HTTPX SSL context, which does not consider system trust roots
        # Users can revert to the HTTPX SSL context with 'verify_ssl=True'
        verify_ssl = verify_ssl or ssl.create_default_context()
        self.kwargs = kwargs

        # Three credential modes for the login service: no creds, login session, and refresh token
        if creds.refresh_token:
            self.client = LoginClient(
                self.base_url,
                cookies={'refresh_token_cookie': creds.refresh_token},
                verify_ssl=verify_ssl,
                **kwargs)
            if self.httpx_client is not None:
                self.httpx_client.cookies.set('refresh_token_cookie', creds.refresh_token)
                self.client.set_httpx_client(self.httpx_client)
        elif login_session_creds:
            self.login_client = LoginAuthenticatedClient(
                self.base_url,
                token=login_session_creds.access_token,
                verify_ssl=verify_ssl,
                **kwargs)
            if self.httpx_client is not None:
                self.httpx_client.headers[self.login_client.auth_header_name] = (
                    f"{self.login_client.prefix} {self.login_client.token}" if self.login_client.prefix else self.login_client.token
                )
                self.login_client.set_httpx_client(self.httpx_client)
        else:
            self.login_client = LoginClient(
                self.base_url,
                verify_ssl=verify_ssl,
                **kwargs)
            if self.httpx_client is not None:
                self.login_client.set_httpx_client(self.httpx_client)


    def get_instances(self):
        if not self.creds or not self.creds.refresh_token:
            raise ValueError("get_instances requires a refresh token.")
        response = get_instances_api_v1_login_get_instances_post(client=self.client)
        response = response.parsed
        if not response:
            raise RemoteError(f"Unable to connect to {self.base_url}")
        if isinstance(response, models.ChallengeResponse):
            raise AuthorizationException(f"{response.title}: {response.detail}")
        if not isinstance(response, list):
            raise RemoteError(response)
        return response

    def to_instance_sdk(self, verify_ssl: str | bool | ssl.SSLContext = True, **kwargs):
        if not self.creds or not self.creds.refresh_token or not self.creds.organization_name:
            raise ValueError("to_instance_sdk requires a refresh token and organization name.")
        base_url = Invariant.app_base_url(self.base_url)
        client = LoginClient(
            base_url,
            cookies={'refresh_token_cookie': self.creds.refresh_token},
            verify_ssl=verify_ssl,
            **kwargs)
        if self.httpx_client is not None:
            client.set_httpx_client(self.httpx_client)
            self.httpx_client.cookies.set('refresh_token_cookie', self.creds.refresh_token)

        response = refresh_organization_name_api_v1_refresh_post(organization_name=self.creds.organization_name, client=client)
        response = response.parsed
        if not response:
            raise RemoteError(f"Unable to connect to {self.base_url}")
        if isinstance(response, models.ChallengeResponse):
            raise AuthorizationException(f"{response.title}: {response.detail}")
        if not isinstance(response, models.RefreshResponse):
            raise RemoteError(response)

        new_creds = AccessCredential(
            response.access_token,
            refresh_token=self.creds.refresh_token,
            organization_name=self.creds.organization_name)
        return Invariant(
            creds=new_creds,
            settings=self.settings,
            base_url=self.base_url,
            verify_ssl=verify_ssl,
            httpx_client=self.httpx_client,
            **self.kwargs)

import ssl
from typing import Optional

import httpx
from invariant_client import pysdk

from invariant_client.pysdk import AccessCredential, RemoteError

from invariant_client.bindings.invariant_login_client import models
from invariant_client.bindings.invariant_login_client.client import AuthenticatedClient as LoginAuthenticatedClient, Client as LoginClient
from invariant_client.bindings.invariant_login_client.api.login.get_version_api_v1_login_version_get import sync_detailed as get_version_api_v1_login_version_get


class VersionClient:
    """Connect to the server and get the current version."""

    client_base_url: str
    client_kwargs: dict
    httpx_client: Optional[httpx.Client]

    def __init__(self,
            base_url: Optional[str] = None,
            verify_ssl: Optional[str | bool | ssl.SSLContext] = None,
            httpx_client: Optional[httpx.Client] = None,
            **kwargs,
        ):
        self.client_base_url = base_url or pysdk.DOMAIN_NAME
        self.client_kwargs = {}
        self.client_kwargs.update(kwargs)
        self.client_kwargs['verify_ssl'] = verify_ssl
        self.httpx_client = httpx_client

    def get_version(self) -> str:
        """Connect to invariant.tech and get the current version."""
        client = LoginClient(self.client_base_url, **self.client_kwargs)
        if self.httpx_client is not None:
            client.set_httpx_client(self.httpx_client)
        response = get_version_api_v1_login_version_get(client=client)
        response = response.parsed
        if not response:
            raise RemoteError(f"Unable to connect to {self.client_base_url}")
        if not isinstance(response, models.GetVersionResponse):
            raise RemoteError(response)
        return response.version

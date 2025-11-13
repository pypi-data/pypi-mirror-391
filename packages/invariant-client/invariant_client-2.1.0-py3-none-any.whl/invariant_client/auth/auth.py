# Invariant client authentication library


from dataclasses import dataclass
import enum
import ssl
from typing import Optional

import httpx
from invariant_client import pysdk

from invariant_client.pysdk import AccessCredential, RemoteError

from invariant_client.bindings.invariant_login_client import models
from invariant_client.bindings.invariant_login_client.client import AuthenticatedClient as LoginAuthenticatedClient, Client as LoginClient
from invariant_client.bindings.invariant_login_client.api.client_login.init_client_login_api_v1_client_login_post import sync_detailed as init_client_login_api_v1_client_login_post
from invariant_client.bindings.invariant_login_client.api.client_login.consume_client_login_api_v1_client_login_consume_post import sync_detailed as consume_client_login_api_v1_client_login_consume_post


class Unauthorized(Exception):
    """Credentials are not valid."""


class BrowserLoginFlowState(enum.Enum):
    START = enum.auto()
    AWAIT_BROWSER = enum.auto()
    COMPLETE = enum.auto()


class BrowserLoginFlow:
    """ In the browser login flow, the client initiates the login flow, recieves a code (or URL),
    sends the user to the Invariant website in their browser to complete the flow, then
    polls for a response from the server. The server response will contain the CLI
    access control credentials."""

    state: BrowserLoginFlowState
    client_base_url: str
    client_kwargs: dict
    pin_url: Optional[str]         # The PIN code is shared with the user
    client_token: Optional[str]   # The client session token can consume the client login session once fulfilled by the user
    error: Optional[Exception]
    creds: Optional[AccessCredential]   # Successfully gained access_token creds go here
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
        self.state = BrowserLoginFlowState.START
        self.pin_url = None
        self.client_token = None
        self.error = None
        self.creds = None

    def start(self) -> str:
        """Connect to invariant.tech and initiate a browser login flow.
        
        Returns an external login code (string). The user should use this code to complete the login flow
        in their browser."""
        client = LoginClient(self.client_base_url, **self.client_kwargs)
        if self.httpx_client is not None:
            client.set_httpx_client(self.httpx_client)
        response = init_client_login_api_v1_client_login_post(client=client)
        response = response.parsed
        if not response:
            raise RemoteError(f"Unable to connect to {self.client_base_url}")
        if not isinstance(response, models.CreateClientLoginSessionResponse):
            raise RemoteError(response)
        self.state = BrowserLoginFlowState.AWAIT_BROWSER
        self.pin_url = response.url
        self.client_token = response.token
        return self.pin_url

    def poll_await_browser_creds(self) -> Optional[AccessCredential | str]:
        client = LoginAuthenticatedClient(
            self.client_base_url,
            token=self.client_token,
            **self.client_kwargs)
        if self.httpx_client is not None:
            self.httpx_client.headers[client.auth_header_name] = (
                f"{client.prefix} {client.token}" if client.prefix else client.token
            )
            client.set_httpx_client(self.httpx_client)
        response = consume_client_login_api_v1_client_login_consume_post(client=client)
        response = response.parsed
        if not response:
            raise RemoteError(f"Unable to connect to {self.client_base_url}")
        if not isinstance(response, models.ConsumeClientLoginSessionResponse):
            raise RemoteError(response)

        if response.access_token:
            self.creds = AccessCredential(
                access_token=response.access_token,
                refresh_token=None,
                organization_name=response.org_name
            )
            self.state = BrowserLoginFlowState.COMPLETE
            return self.creds
        elif response.retry_after:
            return int(response.retry_after)
        else:
            return 10


    @property
    def success(self):
        return self.state == BrowserLoginFlowState.COMPLETE and self.error is None


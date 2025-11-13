from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.base_error_response import BaseErrorResponse
from ...models.challenge_response import ChallengeResponse
from ...models.create_login_request import CreateLoginRequest
from ...models.email_password_login_request import EmailPasswordLoginRequest
from ...models.init_login_invitation_request import InitLoginInvitationRequest
from ...models.init_login_request import InitLoginRequest
from ...models.init_login_setup_link_request import InitLoginSetupLinkRequest
from ...models.new_password_request import NewPasswordRequest
from ...models.open_id_login_request import OpenIDLoginRequest
from ...models.reset_pin_request import ResetPINRequest
from ...models.reset_request import ResetRequest
from ...models.setup_code_request import SetupCodeRequest
from ...models.validation_error_response import ValidationErrorResponse
from ...models.validation_request import ValidationRequest
from ...types import Response


def _get_kwargs(
    *,
    body: Union[
        "CreateLoginRequest",
        "EmailPasswordLoginRequest",
        "InitLoginInvitationRequest",
        "InitLoginRequest",
        "InitLoginSetupLinkRequest",
        "NewPasswordRequest",
        "OpenIDLoginRequest",
        "ResetPINRequest",
        "ResetRequest",
        "SetupCodeRequest",
        "ValidationRequest",
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/login/",
    }

    _body: dict[str, Any]
    if isinstance(body, InitLoginRequest):
        _body = body.to_dict()
    elif isinstance(body, SetupCodeRequest):
        _body = body.to_dict()
    elif isinstance(body, InitLoginInvitationRequest):
        _body = body.to_dict()
    elif isinstance(body, InitLoginSetupLinkRequest):
        _body = body.to_dict()
    elif isinstance(body, CreateLoginRequest):
        _body = body.to_dict()
    elif isinstance(body, EmailPasswordLoginRequest):
        _body = body.to_dict()
    elif isinstance(body, OpenIDLoginRequest):
        _body = body.to_dict()
    elif isinstance(body, ResetRequest):
        _body = body.to_dict()
    elif isinstance(body, ResetPINRequest):
        _body = body.to_dict()
    elif isinstance(body, NewPasswordRequest):
        _body = body.to_dict()
    else:
        _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[Any, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]
]:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 422:
        response_422 = ValidationErrorResponse.from_dict(response.json())

        return response_422
    if response.status_code == 401:
        response_401 = ChallengeResponse.from_dict(response.json())

        return response_401
    if response.status_code == 404:
        response_404 = BaseErrorResponse.from_dict(response.json())

        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[Any, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: Union[
        "CreateLoginRequest",
        "EmailPasswordLoginRequest",
        "InitLoginInvitationRequest",
        "InitLoginRequest",
        "InitLoginSetupLinkRequest",
        "NewPasswordRequest",
        "OpenIDLoginRequest",
        "ResetPINRequest",
        "ResetRequest",
        "SetupCodeRequest",
        "ValidationRequest",
    ],
) -> Response[
    Union[Any, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]
]:
    r"""Authenticate and respond to authentication challenges

     The challenge-response workflow API. This API may do one of the following:

    1. Create a login session with a \"next challenge\" for the caller.
    2. Reject an incorrect request.
    3. Issue a refresh token cookie.

    ## Login session

    This API will respond with HTTP status 401 containing a Login Session Token when it needs
    the user to complete additional challenges. The Login Session Token (LST) is a signed JWT
    asserting the state of the user in the login workflow. The client must include the LST in
    their next init_login API call to continue the workflow.

    ## Challenges

    These challenge types may be issued by this API.

    ### Primary authentication

    The user must provide a primary authetication credential in response to challenge `auth`. This could
    include basic authentication
    (username / password) or federated login (OIDC, SAML) or passkey.

    Acceptable methods can include `basic_auth`, `oidc`, etc. OIDC may be accompanied by provider
    config info.

    ### Email validation

    The user must retrieve a verification code (PIN) from their email to prove they have control of
    that email account as part of initial account setup in response to challenge `validate_email`.

    ### Setup code

    The user must provide a setup code transmitted from the administrator through some means in
    response to challenge 'setup_code' as part of initial account setup.

    ### New password

    The user must provide a new password as part of initial account setup in response to challenge
    `new_password`. Relevant only if basic_auth is supported.

    ### Password reset PIN

    The user must retrieve a verification code (PIN) from their email to prove they have control of
    that email account in order to proceed with password reset in response to challenge `reset_pin`.

    ### Start challenge

    The client should display the email selection screen. This challenge is typically issued when the
    user session has expired.

    ## Initiating the login process

    The client can initiate a login session using the following message types.

    ### Initialize login

    The basic scenario where the user provides an email address. The server will reply with
    challenge `auth` and a list of available login methods if a login exists for this email.

    ### Consume setup link

    In this scenario the client provides an email address and a setup link. The server will
    confirm the validity of the setup link and allow the session to proceed.

    ## Cookie and cookie session

    This API will issue a refresh token cookie upon successful login. The cookie is linked to
    a cookie session in the database (table user_sessions). The cookie expires after 24 hours
    and cannot be refreshed or extended. The user session auto-expires after a period of inactivity.

    The refresh token cookie is accepted by the following notable APIs:

    -   Get a list of available instances: /get_instances .
    -   Get an instance access token: /:org/api/v1/refresh .
    -   Log out /logout .

    Args:
        body (Union['CreateLoginRequest', 'EmailPasswordLoginRequest',
            'InitLoginInvitationRequest', 'InitLoginRequest', 'InitLoginSetupLinkRequest',
            'NewPasswordRequest', 'OpenIDLoginRequest', 'ResetPINRequest', 'ResetRequest',
            'SetupCodeRequest', 'ValidationRequest']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: Union[
        "CreateLoginRequest",
        "EmailPasswordLoginRequest",
        "InitLoginInvitationRequest",
        "InitLoginRequest",
        "InitLoginSetupLinkRequest",
        "NewPasswordRequest",
        "OpenIDLoginRequest",
        "ResetPINRequest",
        "ResetRequest",
        "SetupCodeRequest",
        "ValidationRequest",
    ],
) -> Optional[
    Union[Any, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]
]:
    r"""Authenticate and respond to authentication challenges

     The challenge-response workflow API. This API may do one of the following:

    1. Create a login session with a \"next challenge\" for the caller.
    2. Reject an incorrect request.
    3. Issue a refresh token cookie.

    ## Login session

    This API will respond with HTTP status 401 containing a Login Session Token when it needs
    the user to complete additional challenges. The Login Session Token (LST) is a signed JWT
    asserting the state of the user in the login workflow. The client must include the LST in
    their next init_login API call to continue the workflow.

    ## Challenges

    These challenge types may be issued by this API.

    ### Primary authentication

    The user must provide a primary authetication credential in response to challenge `auth`. This could
    include basic authentication
    (username / password) or federated login (OIDC, SAML) or passkey.

    Acceptable methods can include `basic_auth`, `oidc`, etc. OIDC may be accompanied by provider
    config info.

    ### Email validation

    The user must retrieve a verification code (PIN) from their email to prove they have control of
    that email account as part of initial account setup in response to challenge `validate_email`.

    ### Setup code

    The user must provide a setup code transmitted from the administrator through some means in
    response to challenge 'setup_code' as part of initial account setup.

    ### New password

    The user must provide a new password as part of initial account setup in response to challenge
    `new_password`. Relevant only if basic_auth is supported.

    ### Password reset PIN

    The user must retrieve a verification code (PIN) from their email to prove they have control of
    that email account in order to proceed with password reset in response to challenge `reset_pin`.

    ### Start challenge

    The client should display the email selection screen. This challenge is typically issued when the
    user session has expired.

    ## Initiating the login process

    The client can initiate a login session using the following message types.

    ### Initialize login

    The basic scenario where the user provides an email address. The server will reply with
    challenge `auth` and a list of available login methods if a login exists for this email.

    ### Consume setup link

    In this scenario the client provides an email address and a setup link. The server will
    confirm the validity of the setup link and allow the session to proceed.

    ## Cookie and cookie session

    This API will issue a refresh token cookie upon successful login. The cookie is linked to
    a cookie session in the database (table user_sessions). The cookie expires after 24 hours
    and cannot be refreshed or extended. The user session auto-expires after a period of inactivity.

    The refresh token cookie is accepted by the following notable APIs:

    -   Get a list of available instances: /get_instances .
    -   Get an instance access token: /:org/api/v1/refresh .
    -   Log out /logout .

    Args:
        body (Union['CreateLoginRequest', 'EmailPasswordLoginRequest',
            'InitLoginInvitationRequest', 'InitLoginRequest', 'InitLoginSetupLinkRequest',
            'NewPasswordRequest', 'OpenIDLoginRequest', 'ResetPINRequest', 'ResetRequest',
            'SetupCodeRequest', 'ValidationRequest']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: Union[
        "CreateLoginRequest",
        "EmailPasswordLoginRequest",
        "InitLoginInvitationRequest",
        "InitLoginRequest",
        "InitLoginSetupLinkRequest",
        "NewPasswordRequest",
        "OpenIDLoginRequest",
        "ResetPINRequest",
        "ResetRequest",
        "SetupCodeRequest",
        "ValidationRequest",
    ],
) -> Response[
    Union[Any, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]
]:
    r"""Authenticate and respond to authentication challenges

     The challenge-response workflow API. This API may do one of the following:

    1. Create a login session with a \"next challenge\" for the caller.
    2. Reject an incorrect request.
    3. Issue a refresh token cookie.

    ## Login session

    This API will respond with HTTP status 401 containing a Login Session Token when it needs
    the user to complete additional challenges. The Login Session Token (LST) is a signed JWT
    asserting the state of the user in the login workflow. The client must include the LST in
    their next init_login API call to continue the workflow.

    ## Challenges

    These challenge types may be issued by this API.

    ### Primary authentication

    The user must provide a primary authetication credential in response to challenge `auth`. This could
    include basic authentication
    (username / password) or federated login (OIDC, SAML) or passkey.

    Acceptable methods can include `basic_auth`, `oidc`, etc. OIDC may be accompanied by provider
    config info.

    ### Email validation

    The user must retrieve a verification code (PIN) from their email to prove they have control of
    that email account as part of initial account setup in response to challenge `validate_email`.

    ### Setup code

    The user must provide a setup code transmitted from the administrator through some means in
    response to challenge 'setup_code' as part of initial account setup.

    ### New password

    The user must provide a new password as part of initial account setup in response to challenge
    `new_password`. Relevant only if basic_auth is supported.

    ### Password reset PIN

    The user must retrieve a verification code (PIN) from their email to prove they have control of
    that email account in order to proceed with password reset in response to challenge `reset_pin`.

    ### Start challenge

    The client should display the email selection screen. This challenge is typically issued when the
    user session has expired.

    ## Initiating the login process

    The client can initiate a login session using the following message types.

    ### Initialize login

    The basic scenario where the user provides an email address. The server will reply with
    challenge `auth` and a list of available login methods if a login exists for this email.

    ### Consume setup link

    In this scenario the client provides an email address and a setup link. The server will
    confirm the validity of the setup link and allow the session to proceed.

    ## Cookie and cookie session

    This API will issue a refresh token cookie upon successful login. The cookie is linked to
    a cookie session in the database (table user_sessions). The cookie expires after 24 hours
    and cannot be refreshed or extended. The user session auto-expires after a period of inactivity.

    The refresh token cookie is accepted by the following notable APIs:

    -   Get a list of available instances: /get_instances .
    -   Get an instance access token: /:org/api/v1/refresh .
    -   Log out /logout .

    Args:
        body (Union['CreateLoginRequest', 'EmailPasswordLoginRequest',
            'InitLoginInvitationRequest', 'InitLoginRequest', 'InitLoginSetupLinkRequest',
            'NewPasswordRequest', 'OpenIDLoginRequest', 'ResetPINRequest', 'ResetRequest',
            'SetupCodeRequest', 'ValidationRequest']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: Union[
        "CreateLoginRequest",
        "EmailPasswordLoginRequest",
        "InitLoginInvitationRequest",
        "InitLoginRequest",
        "InitLoginSetupLinkRequest",
        "NewPasswordRequest",
        "OpenIDLoginRequest",
        "ResetPINRequest",
        "ResetRequest",
        "SetupCodeRequest",
        "ValidationRequest",
    ],
) -> Optional[
    Union[Any, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]
]:
    r"""Authenticate and respond to authentication challenges

     The challenge-response workflow API. This API may do one of the following:

    1. Create a login session with a \"next challenge\" for the caller.
    2. Reject an incorrect request.
    3. Issue a refresh token cookie.

    ## Login session

    This API will respond with HTTP status 401 containing a Login Session Token when it needs
    the user to complete additional challenges. The Login Session Token (LST) is a signed JWT
    asserting the state of the user in the login workflow. The client must include the LST in
    their next init_login API call to continue the workflow.

    ## Challenges

    These challenge types may be issued by this API.

    ### Primary authentication

    The user must provide a primary authetication credential in response to challenge `auth`. This could
    include basic authentication
    (username / password) or federated login (OIDC, SAML) or passkey.

    Acceptable methods can include `basic_auth`, `oidc`, etc. OIDC may be accompanied by provider
    config info.

    ### Email validation

    The user must retrieve a verification code (PIN) from their email to prove they have control of
    that email account as part of initial account setup in response to challenge `validate_email`.

    ### Setup code

    The user must provide a setup code transmitted from the administrator through some means in
    response to challenge 'setup_code' as part of initial account setup.

    ### New password

    The user must provide a new password as part of initial account setup in response to challenge
    `new_password`. Relevant only if basic_auth is supported.

    ### Password reset PIN

    The user must retrieve a verification code (PIN) from their email to prove they have control of
    that email account in order to proceed with password reset in response to challenge `reset_pin`.

    ### Start challenge

    The client should display the email selection screen. This challenge is typically issued when the
    user session has expired.

    ## Initiating the login process

    The client can initiate a login session using the following message types.

    ### Initialize login

    The basic scenario where the user provides an email address. The server will reply with
    challenge `auth` and a list of available login methods if a login exists for this email.

    ### Consume setup link

    In this scenario the client provides an email address and a setup link. The server will
    confirm the validity of the setup link and allow the session to proceed.

    ## Cookie and cookie session

    This API will issue a refresh token cookie upon successful login. The cookie is linked to
    a cookie session in the database (table user_sessions). The cookie expires after 24 hours
    and cannot be refreshed or extended. The user session auto-expires after a period of inactivity.

    The refresh token cookie is accepted by the following notable APIs:

    -   Get a list of available instances: /get_instances .
    -   Get an instance access token: /:org/api/v1/refresh .
    -   Log out /logout .

    Args:
        body (Union['CreateLoginRequest', 'EmailPasswordLoginRequest',
            'InitLoginInvitationRequest', 'InitLoginRequest', 'InitLoginSetupLinkRequest',
            'NewPasswordRequest', 'OpenIDLoginRequest', 'ResetPINRequest', 'ResetRequest',
            'SetupCodeRequest', 'ValidationRequest']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed

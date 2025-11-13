from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.base_error_response import BaseErrorResponse
from ...models.challenge_response import ChallengeResponse
from ...models.create_managed_user_request import CreateManagedUserRequest
from ...models.create_member_response import CreateMemberResponse
from ...models.create_service_account_request import CreateServiceAccountRequest
from ...models.create_service_account_response import CreateServiceAccountResponse
from ...models.invite_response import InviteResponse
from ...models.invite_user_request import InviteUserRequest
from ...models.validation_error_response import ValidationErrorResponse
from ...types import Response


def _get_kwargs(
    organization_name: str,
    *,
    body: Union[
        "CreateManagedUserRequest", "CreateServiceAccountRequest", "InviteUserRequest"
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/{organization_name}/api/v1/members/".format(
            organization_name=organization_name,
        ),
    }

    _body: dict[str, Any]
    if isinstance(body, CreateManagedUserRequest):
        _body = body.to_dict()
    elif isinstance(body, InviteUserRequest):
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
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        Union["CreateMemberResponse", "CreateServiceAccountResponse", "InviteResponse"],
        ValidationErrorResponse,
    ]
]:
    if response.status_code == 200:

        def _parse_response_200(
            data: object,
        ) -> Union[
            "CreateMemberResponse", "CreateServiceAccountResponse", "InviteResponse"
        ]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200_type_0 = CreateMemberResponse.from_dict(data)

                return response_200_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200_type_1 = InviteResponse.from_dict(data)

                return response_200_type_1
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            response_200_type_2 = CreateServiceAccountResponse.from_dict(data)

            return response_200_type_2

        response_200 = _parse_response_200(response.json())

        return response_200
    if response.status_code == 422:
        response_422 = ValidationErrorResponse.from_dict(response.json())

        return response_422
    if response.status_code == 400:
        response_400 = BaseErrorResponse.from_dict(response.json())

        return response_400
    if response.status_code == 401:
        response_401 = ChallengeResponse.from_dict(response.json())

        return response_401
    if response.status_code == 404:
        response_404 = BaseErrorResponse.from_dict(response.json())

        return response_404
    if response.status_code == 409:
        response_409 = BaseErrorResponse.from_dict(response.json())

        return response_409
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        Union["CreateMemberResponse", "CreateServiceAccountResponse", "InviteResponse"],
        ValidationErrorResponse,
    ]
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization_name: str,
    *,
    client: AuthenticatedClient,
    body: Union[
        "CreateManagedUserRequest", "CreateServiceAccountRequest", "InviteUserRequest"
    ],
) -> Response[
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        Union["CreateMemberResponse", "CreateServiceAccountResponse", "InviteResponse"],
        ValidationErrorResponse,
    ]
]:
    """Create or invite user

     Create or invite a user in the organization. Creating a user creates a 'managed user', a whole user
    account managed by this organization. An invited user is not managed by this organization. You can
    disallow outside user invitations in the security settings.

    Args:
        organization_name (str):
        body (Union['CreateManagedUserRequest', 'CreateServiceAccountRequest',
            'InviteUserRequest']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseErrorResponse, ChallengeResponse, Union['CreateMemberResponse', 'CreateServiceAccountResponse', 'InviteResponse'], ValidationErrorResponse]]
    """

    kwargs = _get_kwargs(
        organization_name=organization_name,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_name: str,
    *,
    client: AuthenticatedClient,
    body: Union[
        "CreateManagedUserRequest", "CreateServiceAccountRequest", "InviteUserRequest"
    ],
) -> Optional[
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        Union["CreateMemberResponse", "CreateServiceAccountResponse", "InviteResponse"],
        ValidationErrorResponse,
    ]
]:
    """Create or invite user

     Create or invite a user in the organization. Creating a user creates a 'managed user', a whole user
    account managed by this organization. An invited user is not managed by this organization. You can
    disallow outside user invitations in the security settings.

    Args:
        organization_name (str):
        body (Union['CreateManagedUserRequest', 'CreateServiceAccountRequest',
            'InviteUserRequest']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseErrorResponse, ChallengeResponse, Union['CreateMemberResponse', 'CreateServiceAccountResponse', 'InviteResponse'], ValidationErrorResponse]
    """

    return sync_detailed(
        organization_name=organization_name,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    organization_name: str,
    *,
    client: AuthenticatedClient,
    body: Union[
        "CreateManagedUserRequest", "CreateServiceAccountRequest", "InviteUserRequest"
    ],
) -> Response[
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        Union["CreateMemberResponse", "CreateServiceAccountResponse", "InviteResponse"],
        ValidationErrorResponse,
    ]
]:
    """Create or invite user

     Create or invite a user in the organization. Creating a user creates a 'managed user', a whole user
    account managed by this organization. An invited user is not managed by this organization. You can
    disallow outside user invitations in the security settings.

    Args:
        organization_name (str):
        body (Union['CreateManagedUserRequest', 'CreateServiceAccountRequest',
            'InviteUserRequest']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseErrorResponse, ChallengeResponse, Union['CreateMemberResponse', 'CreateServiceAccountResponse', 'InviteResponse'], ValidationErrorResponse]]
    """

    kwargs = _get_kwargs(
        organization_name=organization_name,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_name: str,
    *,
    client: AuthenticatedClient,
    body: Union[
        "CreateManagedUserRequest", "CreateServiceAccountRequest", "InviteUserRequest"
    ],
) -> Optional[
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        Union["CreateMemberResponse", "CreateServiceAccountResponse", "InviteResponse"],
        ValidationErrorResponse,
    ]
]:
    """Create or invite user

     Create or invite a user in the organization. Creating a user creates a 'managed user', a whole user
    account managed by this organization. An invited user is not managed by this organization. You can
    disallow outside user invitations in the security settings.

    Args:
        organization_name (str):
        body (Union['CreateManagedUserRequest', 'CreateServiceAccountRequest',
            'InviteUserRequest']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseErrorResponse, ChallengeResponse, Union['CreateMemberResponse', 'CreateServiceAccountResponse', 'InviteResponse'], ValidationErrorResponse]
    """

    return (
        await asyncio_detailed(
            organization_name=organization_name,
            client=client,
            body=body,
        )
    ).parsed

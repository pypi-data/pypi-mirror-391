import datetime
from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.base_error_response import BaseErrorResponse
from ...models.challenge_response import ChallengeResponse
from ...models.list_usage_response import ListUsageResponse
from ...models.validation_error_response import ValidationErrorResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization_name: str,
    *,
    network_uuid: Union[None, UUID, Unset] = UNSET,
    limit: Union[Unset, int] = 100,
    before_created_at: Union[None, Unset, datetime.datetime] = UNSET,
    before_exec_uuid: Union[None, UUID, Unset] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_network_uuid: Union[None, Unset, str]
    if isinstance(network_uuid, Unset):
        json_network_uuid = UNSET
    elif isinstance(network_uuid, UUID):
        json_network_uuid = str(network_uuid)
    else:
        json_network_uuid = network_uuid
    params["network_uuid"] = json_network_uuid

    params["limit"] = limit

    json_before_created_at: Union[None, Unset, str]
    if isinstance(before_created_at, Unset):
        json_before_created_at = UNSET
    elif isinstance(before_created_at, datetime.datetime):
        json_before_created_at = before_created_at.isoformat()
    else:
        json_before_created_at = before_created_at
    params["before_created_at"] = json_before_created_at

    json_before_exec_uuid: Union[None, Unset, str]
    if isinstance(before_exec_uuid, Unset):
        json_before_exec_uuid = UNSET
    elif isinstance(before_exec_uuid, UUID):
        json_before_exec_uuid = str(before_exec_uuid)
    else:
        json_before_exec_uuid = before_exec_uuid
    params["before_exec_uuid"] = json_before_exec_uuid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/{organization_name}/api/v1/usage/".format(
            organization_name=organization_name,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        BaseErrorResponse, ChallengeResponse, ListUsageResponse, ValidationErrorResponse
    ]
]:
    if response.status_code == 200:
        response_200 = ListUsageResponse.from_dict(response.json())

        return response_200
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
    Union[
        BaseErrorResponse, ChallengeResponse, ListUsageResponse, ValidationErrorResponse
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
    network_uuid: Union[None, UUID, Unset] = UNSET,
    limit: Union[Unset, int] = 100,
    before_created_at: Union[None, Unset, datetime.datetime] = UNSET,
    before_exec_uuid: Union[None, UUID, Unset] = UNSET,
) -> Response[
    Union[
        BaseErrorResponse, ChallengeResponse, ListUsageResponse, ValidationErrorResponse
    ]
]:
    """List Usage Events

     List usage events for an organization.

    Args:
        organization_name (str):
        network_uuid (Union[None, UUID, Unset]):
        limit (Union[Unset, int]):  Default: 100.
        before_created_at (Union[None, Unset, datetime.datetime]):
        before_exec_uuid (Union[None, UUID, Unset]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseErrorResponse, ChallengeResponse, ListUsageResponse, ValidationErrorResponse]]
    """

    kwargs = _get_kwargs(
        organization_name=organization_name,
        network_uuid=network_uuid,
        limit=limit,
        before_created_at=before_created_at,
        before_exec_uuid=before_exec_uuid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_name: str,
    *,
    client: AuthenticatedClient,
    network_uuid: Union[None, UUID, Unset] = UNSET,
    limit: Union[Unset, int] = 100,
    before_created_at: Union[None, Unset, datetime.datetime] = UNSET,
    before_exec_uuid: Union[None, UUID, Unset] = UNSET,
) -> Optional[
    Union[
        BaseErrorResponse, ChallengeResponse, ListUsageResponse, ValidationErrorResponse
    ]
]:
    """List Usage Events

     List usage events for an organization.

    Args:
        organization_name (str):
        network_uuid (Union[None, UUID, Unset]):
        limit (Union[Unset, int]):  Default: 100.
        before_created_at (Union[None, Unset, datetime.datetime]):
        before_exec_uuid (Union[None, UUID, Unset]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseErrorResponse, ChallengeResponse, ListUsageResponse, ValidationErrorResponse]
    """

    return sync_detailed(
        organization_name=organization_name,
        client=client,
        network_uuid=network_uuid,
        limit=limit,
        before_created_at=before_created_at,
        before_exec_uuid=before_exec_uuid,
    ).parsed


async def asyncio_detailed(
    organization_name: str,
    *,
    client: AuthenticatedClient,
    network_uuid: Union[None, UUID, Unset] = UNSET,
    limit: Union[Unset, int] = 100,
    before_created_at: Union[None, Unset, datetime.datetime] = UNSET,
    before_exec_uuid: Union[None, UUID, Unset] = UNSET,
) -> Response[
    Union[
        BaseErrorResponse, ChallengeResponse, ListUsageResponse, ValidationErrorResponse
    ]
]:
    """List Usage Events

     List usage events for an organization.

    Args:
        organization_name (str):
        network_uuid (Union[None, UUID, Unset]):
        limit (Union[Unset, int]):  Default: 100.
        before_created_at (Union[None, Unset, datetime.datetime]):
        before_exec_uuid (Union[None, UUID, Unset]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseErrorResponse, ChallengeResponse, ListUsageResponse, ValidationErrorResponse]]
    """

    kwargs = _get_kwargs(
        organization_name=organization_name,
        network_uuid=network_uuid,
        limit=limit,
        before_created_at=before_created_at,
        before_exec_uuid=before_exec_uuid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_name: str,
    *,
    client: AuthenticatedClient,
    network_uuid: Union[None, UUID, Unset] = UNSET,
    limit: Union[Unset, int] = 100,
    before_created_at: Union[None, Unset, datetime.datetime] = UNSET,
    before_exec_uuid: Union[None, UUID, Unset] = UNSET,
) -> Optional[
    Union[
        BaseErrorResponse, ChallengeResponse, ListUsageResponse, ValidationErrorResponse
    ]
]:
    """List Usage Events

     List usage events for an organization.

    Args:
        organization_name (str):
        network_uuid (Union[None, UUID, Unset]):
        limit (Union[Unset, int]):  Default: 100.
        before_created_at (Union[None, Unset, datetime.datetime]):
        before_exec_uuid (Union[None, UUID, Unset]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseErrorResponse, ChallengeResponse, ListUsageResponse, ValidationErrorResponse]
    """

    return (
        await asyncio_detailed(
            organization_name=organization_name,
            client=client,
            network_uuid=network_uuid,
            limit=limit,
            before_created_at=before_created_at,
            before_exec_uuid=before_exec_uuid,
        )
    ).parsed

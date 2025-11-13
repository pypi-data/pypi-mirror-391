from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.base_error_response import BaseErrorResponse
from ...models.challenge_response import ChallengeResponse
from ...models.list_networks_with_extras_response import ListNetworksWithExtrasResponse
from ...models.validation_error_response import ValidationErrorResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization_name: str,
    *,
    limit: Union[None, Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_limit: Union[None, Unset, int]
    if isinstance(limit, Unset):
        json_limit = UNSET
    else:
        json_limit = limit
    params["limit"] = json_limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/{organization_name}/api/v1/networks/extras".format(
            organization_name=organization_name,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        ListNetworksWithExtrasResponse,
        ValidationErrorResponse,
    ]
]:
    if response.status_code == 200:
        response_200 = ListNetworksWithExtrasResponse.from_dict(response.json())

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
        BaseErrorResponse,
        ChallengeResponse,
        ListNetworksWithExtrasResponse,
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
    limit: Union[None, Unset, int] = UNSET,
) -> Response[
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        ListNetworksWithExtrasResponse,
        ValidationErrorResponse,
    ]
]:
    """List Networks With Extras

    Args:
        organization_name (str):
        limit (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseErrorResponse, ChallengeResponse, ListNetworksWithExtrasResponse, ValidationErrorResponse]]
    """

    kwargs = _get_kwargs(
        organization_name=organization_name,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_name: str,
    *,
    client: AuthenticatedClient,
    limit: Union[None, Unset, int] = UNSET,
) -> Optional[
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        ListNetworksWithExtrasResponse,
        ValidationErrorResponse,
    ]
]:
    """List Networks With Extras

    Args:
        organization_name (str):
        limit (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseErrorResponse, ChallengeResponse, ListNetworksWithExtrasResponse, ValidationErrorResponse]
    """

    return sync_detailed(
        organization_name=organization_name,
        client=client,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    organization_name: str,
    *,
    client: AuthenticatedClient,
    limit: Union[None, Unset, int] = UNSET,
) -> Response[
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        ListNetworksWithExtrasResponse,
        ValidationErrorResponse,
    ]
]:
    """List Networks With Extras

    Args:
        organization_name (str):
        limit (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseErrorResponse, ChallengeResponse, ListNetworksWithExtrasResponse, ValidationErrorResponse]]
    """

    kwargs = _get_kwargs(
        organization_name=organization_name,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_name: str,
    *,
    client: AuthenticatedClient,
    limit: Union[None, Unset, int] = UNSET,
) -> Optional[
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        ListNetworksWithExtrasResponse,
        ValidationErrorResponse,
    ]
]:
    """List Networks With Extras

    Args:
        organization_name (str):
        limit (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseErrorResponse, ChallengeResponse, ListNetworksWithExtrasResponse, ValidationErrorResponse]
    """

    return (
        await asyncio_detailed(
            organization_name=organization_name,
            client=client,
            limit=limit,
        )
    ).parsed

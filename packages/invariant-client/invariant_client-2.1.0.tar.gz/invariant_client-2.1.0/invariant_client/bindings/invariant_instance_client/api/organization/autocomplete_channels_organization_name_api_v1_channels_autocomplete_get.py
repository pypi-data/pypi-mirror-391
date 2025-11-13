from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.validation_error_response import ValidationErrorResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization_name: str,
    *,
    q: Union[None, Unset, str] = UNSET,
    team_id: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_q: Union[None, Unset, str]
    if isinstance(q, Unset):
        json_q = UNSET
    else:
        json_q = q
    params["q"] = json_q

    params["team_id"] = team_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/{organization_name}/api/v1/channels/autocomplete".format(
            organization_name=organization_name,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ValidationErrorResponse, list[str]]]:
    if response.status_code == 200:
        response_200 = cast(list[str], response.json())

        return response_200
    if response.status_code == 422:
        response_422 = ValidationErrorResponse.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[ValidationErrorResponse, list[str]]]:
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
    q: Union[None, Unset, str] = UNSET,
    team_id: Union[Unset, str] = UNSET,
) -> Response[Union[ValidationErrorResponse, list[str]]]:
    """Autocomplete Channels

    Args:
        organization_name (str):
        q (Union[None, Unset, str]):
        team_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ValidationErrorResponse, list[str]]]
    """

    kwargs = _get_kwargs(
        organization_name=organization_name,
        q=q,
        team_id=team_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_name: str,
    *,
    client: AuthenticatedClient,
    q: Union[None, Unset, str] = UNSET,
    team_id: Union[Unset, str] = UNSET,
) -> Optional[Union[ValidationErrorResponse, list[str]]]:
    """Autocomplete Channels

    Args:
        organization_name (str):
        q (Union[None, Unset, str]):
        team_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ValidationErrorResponse, list[str]]
    """

    return sync_detailed(
        organization_name=organization_name,
        client=client,
        q=q,
        team_id=team_id,
    ).parsed


async def asyncio_detailed(
    organization_name: str,
    *,
    client: AuthenticatedClient,
    q: Union[None, Unset, str] = UNSET,
    team_id: Union[Unset, str] = UNSET,
) -> Response[Union[ValidationErrorResponse, list[str]]]:
    """Autocomplete Channels

    Args:
        organization_name (str):
        q (Union[None, Unset, str]):
        team_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ValidationErrorResponse, list[str]]]
    """

    kwargs = _get_kwargs(
        organization_name=organization_name,
        q=q,
        team_id=team_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_name: str,
    *,
    client: AuthenticatedClient,
    q: Union[None, Unset, str] = UNSET,
    team_id: Union[Unset, str] = UNSET,
) -> Optional[Union[ValidationErrorResponse, list[str]]]:
    """Autocomplete Channels

    Args:
        organization_name (str):
        q (Union[None, Unset, str]):
        team_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ValidationErrorResponse, list[str]]
    """

    return (
        await asyncio_detailed(
            organization_name=organization_name,
            client=client,
            q=q,
            team_id=team_id,
        )
    ).parsed

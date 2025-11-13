from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.base_error_response import BaseErrorResponse
from ...models.create_client_login_session_response import (
    CreateClientLoginSessionResponse,
)
from ...models.validation_error_response import ValidationErrorResponse
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/client-login",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[BaseErrorResponse, CreateClientLoginSessionResponse, ValidationErrorResponse]
]:
    if response.status_code == 201:
        response_201 = CreateClientLoginSessionResponse.from_dict(response.json())

        return response_201
    if response.status_code == 422:
        response_422 = ValidationErrorResponse.from_dict(response.json())

        return response_422
    if response.status_code == 500:
        response_500 = BaseErrorResponse.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[BaseErrorResponse, CreateClientLoginSessionResponse, ValidationErrorResponse]
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[
    Union[BaseErrorResponse, CreateClientLoginSessionResponse, ValidationErrorResponse]
]:
    """Create a client login flow token.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseErrorResponse, CreateClientLoginSessionResponse, ValidationErrorResponse]]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[
    Union[BaseErrorResponse, CreateClientLoginSessionResponse, ValidationErrorResponse]
]:
    """Create a client login flow token.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseErrorResponse, CreateClientLoginSessionResponse, ValidationErrorResponse]
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[
    Union[BaseErrorResponse, CreateClientLoginSessionResponse, ValidationErrorResponse]
]:
    """Create a client login flow token.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseErrorResponse, CreateClientLoginSessionResponse, ValidationErrorResponse]]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[
    Union[BaseErrorResponse, CreateClientLoginSessionResponse, ValidationErrorResponse]
]:
    """Create a client login flow token.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseErrorResponse, CreateClientLoginSessionResponse, ValidationErrorResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed

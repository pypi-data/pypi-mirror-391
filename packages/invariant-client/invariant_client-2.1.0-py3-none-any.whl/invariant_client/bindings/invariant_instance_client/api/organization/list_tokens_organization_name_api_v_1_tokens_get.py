from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_token_response import APITokenResponse
from ...models.base_error_response import BaseErrorResponse
from ...models.challenge_response import ChallengeResponse
from ...models.validation_error_response import ValidationErrorResponse
from ...types import Response


def _get_kwargs(
    organization_name: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/{organization_name}/api/v1/tokens/".format(
            organization_name=organization_name,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        APITokenResponse, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse
    ]
]:
    if response.status_code == 200:
        response_200 = APITokenResponse.from_dict(response.json())

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
        APITokenResponse, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse
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
) -> Response[
    Union[
        APITokenResponse, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse
    ]
]:
    """List API Tokens

    Args:
        organization_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[APITokenResponse, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]]
    """

    kwargs = _get_kwargs(
        organization_name=organization_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_name: str,
    *,
    client: AuthenticatedClient,
) -> Optional[
    Union[
        APITokenResponse, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse
    ]
]:
    """List API Tokens

    Args:
        organization_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[APITokenResponse, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]
    """

    return sync_detailed(
        organization_name=organization_name,
        client=client,
    ).parsed


async def asyncio_detailed(
    organization_name: str,
    *,
    client: AuthenticatedClient,
) -> Response[
    Union[
        APITokenResponse, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse
    ]
]:
    """List API Tokens

    Args:
        organization_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[APITokenResponse, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]]
    """

    kwargs = _get_kwargs(
        organization_name=organization_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_name: str,
    *,
    client: AuthenticatedClient,
) -> Optional[
    Union[
        APITokenResponse, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse
    ]
]:
    """List API Tokens

    Args:
        organization_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[APITokenResponse, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]
    """

    return (
        await asyncio_detailed(
            organization_name=organization_name,
            client=client,
        )
    ).parsed

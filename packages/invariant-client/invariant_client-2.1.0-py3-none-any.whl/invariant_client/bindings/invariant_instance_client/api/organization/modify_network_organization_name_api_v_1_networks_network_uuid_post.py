from http import HTTPStatus
from typing import Any, Optional, Union, cast
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.base_error_response import BaseErrorResponse
from ...models.challenge_response import ChallengeResponse
from ...models.modify_network_request import ModifyNetworkRequest
from ...models.validation_error_response import ValidationErrorResponse
from ...types import Response


def _get_kwargs(
    organization_name: str,
    network_uuid: UUID,
    *,
    body: ModifyNetworkRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/{organization_name}/api/v1/networks/{network_uuid}".format(
            organization_name=organization_name,
            network_uuid=network_uuid,
        ),
    }

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
    organization_name: str,
    network_uuid: UUID,
    *,
    client: AuthenticatedClient,
    body: ModifyNetworkRequest,
) -> Response[
    Union[Any, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]
]:
    """Modify Network

    Args:
        organization_name (str):
        network_uuid (UUID):
        body (ModifyNetworkRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]]
    """

    kwargs = _get_kwargs(
        organization_name=organization_name,
        network_uuid=network_uuid,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_name: str,
    network_uuid: UUID,
    *,
    client: AuthenticatedClient,
    body: ModifyNetworkRequest,
) -> Optional[
    Union[Any, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]
]:
    """Modify Network

    Args:
        organization_name (str):
        network_uuid (UUID):
        body (ModifyNetworkRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]
    """

    return sync_detailed(
        organization_name=organization_name,
        network_uuid=network_uuid,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    organization_name: str,
    network_uuid: UUID,
    *,
    client: AuthenticatedClient,
    body: ModifyNetworkRequest,
) -> Response[
    Union[Any, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]
]:
    """Modify Network

    Args:
        organization_name (str):
        network_uuid (UUID):
        body (ModifyNetworkRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]]
    """

    kwargs = _get_kwargs(
        organization_name=organization_name,
        network_uuid=network_uuid,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_name: str,
    network_uuid: UUID,
    *,
    client: AuthenticatedClient,
    body: ModifyNetworkRequest,
) -> Optional[
    Union[Any, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]
]:
    """Modify Network

    Args:
        organization_name (str):
        network_uuid (UUID):
        body (ModifyNetworkRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]
    """

    return (
        await asyncio_detailed(
            organization_name=organization_name,
            network_uuid=network_uuid,
            client=client,
            body=body,
        )
    ).parsed

from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.base_error_response import BaseErrorResponse
from ...models.challenge_response import ChallengeResponse
from ...models.resource_set_with_extras import ResourceSetWithExtras
from ...models.validation_error_response import ValidationErrorResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization_name: str,
    *,
    filter_defaults: Union[Unset, bool] = False,
    filter_named: Union[Unset, bool] = False,
    filter_type: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["filter_defaults"] = filter_defaults

    params["filter_named"] = filter_named

    json_filter_type: Union[None, Unset, str]
    if isinstance(filter_type, Unset):
        json_filter_type = UNSET
    else:
        json_filter_type = filter_type
    params["filter_type"] = json_filter_type

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/{organization_name}/api/v1/resource_sets/".format(
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
        ValidationErrorResponse,
        list["ResourceSetWithExtras"],
    ]
]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ResourceSetWithExtras.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
        ValidationErrorResponse,
        list["ResourceSetWithExtras"],
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
    filter_defaults: Union[Unset, bool] = False,
    filter_named: Union[Unset, bool] = False,
    filter_type: Union[None, Unset, str] = UNSET,
) -> Response[
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        ValidationErrorResponse,
        list["ResourceSetWithExtras"],
    ]
]:
    """List Resource Sets

    Args:
        organization_name (str):
        filter_defaults (Union[Unset, bool]):  Default: False.
        filter_named (Union[Unset, bool]):  Default: False.
        filter_type (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseErrorResponse, ChallengeResponse, ValidationErrorResponse, list['ResourceSetWithExtras']]]
    """

    kwargs = _get_kwargs(
        organization_name=organization_name,
        filter_defaults=filter_defaults,
        filter_named=filter_named,
        filter_type=filter_type,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_name: str,
    *,
    client: AuthenticatedClient,
    filter_defaults: Union[Unset, bool] = False,
    filter_named: Union[Unset, bool] = False,
    filter_type: Union[None, Unset, str] = UNSET,
) -> Optional[
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        ValidationErrorResponse,
        list["ResourceSetWithExtras"],
    ]
]:
    """List Resource Sets

    Args:
        organization_name (str):
        filter_defaults (Union[Unset, bool]):  Default: False.
        filter_named (Union[Unset, bool]):  Default: False.
        filter_type (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseErrorResponse, ChallengeResponse, ValidationErrorResponse, list['ResourceSetWithExtras']]
    """

    return sync_detailed(
        organization_name=organization_name,
        client=client,
        filter_defaults=filter_defaults,
        filter_named=filter_named,
        filter_type=filter_type,
    ).parsed


async def asyncio_detailed(
    organization_name: str,
    *,
    client: AuthenticatedClient,
    filter_defaults: Union[Unset, bool] = False,
    filter_named: Union[Unset, bool] = False,
    filter_type: Union[None, Unset, str] = UNSET,
) -> Response[
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        ValidationErrorResponse,
        list["ResourceSetWithExtras"],
    ]
]:
    """List Resource Sets

    Args:
        organization_name (str):
        filter_defaults (Union[Unset, bool]):  Default: False.
        filter_named (Union[Unset, bool]):  Default: False.
        filter_type (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseErrorResponse, ChallengeResponse, ValidationErrorResponse, list['ResourceSetWithExtras']]]
    """

    kwargs = _get_kwargs(
        organization_name=organization_name,
        filter_defaults=filter_defaults,
        filter_named=filter_named,
        filter_type=filter_type,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_name: str,
    *,
    client: AuthenticatedClient,
    filter_defaults: Union[Unset, bool] = False,
    filter_named: Union[Unset, bool] = False,
    filter_type: Union[None, Unset, str] = UNSET,
) -> Optional[
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        ValidationErrorResponse,
        list["ResourceSetWithExtras"],
    ]
]:
    """List Resource Sets

    Args:
        organization_name (str):
        filter_defaults (Union[Unset, bool]):  Default: False.
        filter_named (Union[Unset, bool]):  Default: False.
        filter_type (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseErrorResponse, ChallengeResponse, ValidationErrorResponse, list['ResourceSetWithExtras']]
    """

    return (
        await asyncio_detailed(
            organization_name=organization_name,
            client=client,
            filter_defaults=filter_defaults,
            filter_named=filter_named,
            filter_type=filter_type,
        )
    ).parsed

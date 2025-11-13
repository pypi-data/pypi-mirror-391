from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.base_error_response import BaseErrorResponse
from ...models.challenge_response import ChallengeResponse
from ...models.list_reports_response import ListReportsResponse
from ...models.validation_error_response import ValidationErrorResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization_name: str,
    *,
    filter_session: Union[None, Unset, int] = 0,
    filter_net: Union[None, Unset, str] = UNSET,
    limit: Union[None, Unset, int] = 0,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_filter_session: Union[None, Unset, int]
    if isinstance(filter_session, Unset):
        json_filter_session = UNSET
    else:
        json_filter_session = filter_session
    params["filter_session"] = json_filter_session

    json_filter_net: Union[None, Unset, str]
    if isinstance(filter_net, Unset):
        json_filter_net = UNSET
    else:
        json_filter_net = filter_net
    params["filter_net"] = json_filter_net

    json_limit: Union[None, Unset, int]
    if isinstance(limit, Unset):
        json_limit = UNSET
    else:
        json_limit = limit
    params["limit"] = json_limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/{organization_name}/api/v1/reports/".format(
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
        ListReportsResponse,
        ValidationErrorResponse,
    ]
]:
    if response.status_code == 200:
        response_200 = ListReportsResponse.from_dict(response.json())

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
        ListReportsResponse,
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
    filter_session: Union[None, Unset, int] = 0,
    filter_net: Union[None, Unset, str] = UNSET,
    limit: Union[None, Unset, int] = 0,
) -> Response[
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        ListReportsResponse,
        ValidationErrorResponse,
    ]
]:
    """List reports

     Reports are the results of evaluating a snapshot or testing a rule. This API lists reports. Each
    report contains a summary listing the result files for this report, plus an extras section
    condensing that information into user-friendly key-value properties.

    Args:
        organization_name (str):
        filter_session (Union[None, Unset, int]):  Default: 0.
        filter_net (Union[None, Unset, str]):
        limit (Union[None, Unset, int]):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseErrorResponse, ChallengeResponse, ListReportsResponse, ValidationErrorResponse]]
    """

    kwargs = _get_kwargs(
        organization_name=organization_name,
        filter_session=filter_session,
        filter_net=filter_net,
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
    filter_session: Union[None, Unset, int] = 0,
    filter_net: Union[None, Unset, str] = UNSET,
    limit: Union[None, Unset, int] = 0,
) -> Optional[
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        ListReportsResponse,
        ValidationErrorResponse,
    ]
]:
    """List reports

     Reports are the results of evaluating a snapshot or testing a rule. This API lists reports. Each
    report contains a summary listing the result files for this report, plus an extras section
    condensing that information into user-friendly key-value properties.

    Args:
        organization_name (str):
        filter_session (Union[None, Unset, int]):  Default: 0.
        filter_net (Union[None, Unset, str]):
        limit (Union[None, Unset, int]):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseErrorResponse, ChallengeResponse, ListReportsResponse, ValidationErrorResponse]
    """

    return sync_detailed(
        organization_name=organization_name,
        client=client,
        filter_session=filter_session,
        filter_net=filter_net,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    organization_name: str,
    *,
    client: AuthenticatedClient,
    filter_session: Union[None, Unset, int] = 0,
    filter_net: Union[None, Unset, str] = UNSET,
    limit: Union[None, Unset, int] = 0,
) -> Response[
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        ListReportsResponse,
        ValidationErrorResponse,
    ]
]:
    """List reports

     Reports are the results of evaluating a snapshot or testing a rule. This API lists reports. Each
    report contains a summary listing the result files for this report, plus an extras section
    condensing that information into user-friendly key-value properties.

    Args:
        organization_name (str):
        filter_session (Union[None, Unset, int]):  Default: 0.
        filter_net (Union[None, Unset, str]):
        limit (Union[None, Unset, int]):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseErrorResponse, ChallengeResponse, ListReportsResponse, ValidationErrorResponse]]
    """

    kwargs = _get_kwargs(
        organization_name=organization_name,
        filter_session=filter_session,
        filter_net=filter_net,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_name: str,
    *,
    client: AuthenticatedClient,
    filter_session: Union[None, Unset, int] = 0,
    filter_net: Union[None, Unset, str] = UNSET,
    limit: Union[None, Unset, int] = 0,
) -> Optional[
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        ListReportsResponse,
        ValidationErrorResponse,
    ]
]:
    """List reports

     Reports are the results of evaluating a snapshot or testing a rule. This API lists reports. Each
    report contains a summary listing the result files for this report, plus an extras section
    condensing that information into user-friendly key-value properties.

    Args:
        organization_name (str):
        filter_session (Union[None, Unset, int]):  Default: 0.
        filter_net (Union[None, Unset, str]):
        limit (Union[None, Unset, int]):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseErrorResponse, ChallengeResponse, ListReportsResponse, ValidationErrorResponse]
    """

    return (
        await asyncio_detailed(
            organization_name=organization_name,
            client=client,
            filter_session=filter_session,
            filter_net=filter_net,
            limit=limit,
        )
    ).parsed

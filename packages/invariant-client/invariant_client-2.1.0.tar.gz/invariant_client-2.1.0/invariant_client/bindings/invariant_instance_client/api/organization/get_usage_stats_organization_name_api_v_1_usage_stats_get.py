import datetime
from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.base_error_response import BaseErrorResponse
from ...models.challenge_response import ChallengeResponse
from ...models.get_usage_stats_organization_name_api_v1_usage_stats_get_period import (
    GetUsageStatsOrganizationNameApiV1UsageStatsGetPeriod,
)
from ...models.usage_stats_response import UsageStatsResponse
from ...models.validation_error_response import ValidationErrorResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization_name: str,
    *,
    period: Union[
        Unset, GetUsageStatsOrganizationNameApiV1UsageStatsGetPeriod
    ] = GetUsageStatsOrganizationNameApiV1UsageStatsGetPeriod.MONTH,
    after: Union[None, Unset, datetime.datetime] = UNSET,
    before: Union[None, Unset, datetime.datetime] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_period: Union[Unset, str] = UNSET
    if not isinstance(period, Unset):
        json_period = period.value

    params["period"] = json_period

    json_after: Union[None, Unset, str]
    if isinstance(after, Unset):
        json_after = UNSET
    elif isinstance(after, datetime.datetime):
        json_after = after.isoformat()
    else:
        json_after = after
    params["after"] = json_after

    json_before: Union[None, Unset, str]
    if isinstance(before, Unset):
        json_before = UNSET
    elif isinstance(before, datetime.datetime):
        json_before = before.isoformat()
    else:
        json_before = before
    params["before"] = json_before

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/{organization_name}/api/v1/usage/stats".format(
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
        UsageStatsResponse,
        ValidationErrorResponse,
    ]
]:
    if response.status_code == 200:
        response_200 = UsageStatsResponse.from_dict(response.json())

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
        UsageStatsResponse,
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
    period: Union[
        Unset, GetUsageStatsOrganizationNameApiV1UsageStatsGetPeriod
    ] = GetUsageStatsOrganizationNameApiV1UsageStatsGetPeriod.MONTH,
    after: Union[None, Unset, datetime.datetime] = UNSET,
    before: Union[None, Unset, datetime.datetime] = UNSET,
) -> Response[
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        UsageStatsResponse,
        ValidationErrorResponse,
    ]
]:
    """Get Usage Statistics

    Args:
        organization_name (str):
        period (Union[Unset, GetUsageStatsOrganizationNameApiV1UsageStatsGetPeriod]):  Default:
            GetUsageStatsOrganizationNameApiV1UsageStatsGetPeriod.MONTH.
        after (Union[None, Unset, datetime.datetime]):
        before (Union[None, Unset, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseErrorResponse, ChallengeResponse, UsageStatsResponse, ValidationErrorResponse]]
    """

    kwargs = _get_kwargs(
        organization_name=organization_name,
        period=period,
        after=after,
        before=before,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_name: str,
    *,
    client: AuthenticatedClient,
    period: Union[
        Unset, GetUsageStatsOrganizationNameApiV1UsageStatsGetPeriod
    ] = GetUsageStatsOrganizationNameApiV1UsageStatsGetPeriod.MONTH,
    after: Union[None, Unset, datetime.datetime] = UNSET,
    before: Union[None, Unset, datetime.datetime] = UNSET,
) -> Optional[
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        UsageStatsResponse,
        ValidationErrorResponse,
    ]
]:
    """Get Usage Statistics

    Args:
        organization_name (str):
        period (Union[Unset, GetUsageStatsOrganizationNameApiV1UsageStatsGetPeriod]):  Default:
            GetUsageStatsOrganizationNameApiV1UsageStatsGetPeriod.MONTH.
        after (Union[None, Unset, datetime.datetime]):
        before (Union[None, Unset, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseErrorResponse, ChallengeResponse, UsageStatsResponse, ValidationErrorResponse]
    """

    return sync_detailed(
        organization_name=organization_name,
        client=client,
        period=period,
        after=after,
        before=before,
    ).parsed


async def asyncio_detailed(
    organization_name: str,
    *,
    client: AuthenticatedClient,
    period: Union[
        Unset, GetUsageStatsOrganizationNameApiV1UsageStatsGetPeriod
    ] = GetUsageStatsOrganizationNameApiV1UsageStatsGetPeriod.MONTH,
    after: Union[None, Unset, datetime.datetime] = UNSET,
    before: Union[None, Unset, datetime.datetime] = UNSET,
) -> Response[
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        UsageStatsResponse,
        ValidationErrorResponse,
    ]
]:
    """Get Usage Statistics

    Args:
        organization_name (str):
        period (Union[Unset, GetUsageStatsOrganizationNameApiV1UsageStatsGetPeriod]):  Default:
            GetUsageStatsOrganizationNameApiV1UsageStatsGetPeriod.MONTH.
        after (Union[None, Unset, datetime.datetime]):
        before (Union[None, Unset, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseErrorResponse, ChallengeResponse, UsageStatsResponse, ValidationErrorResponse]]
    """

    kwargs = _get_kwargs(
        organization_name=organization_name,
        period=period,
        after=after,
        before=before,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_name: str,
    *,
    client: AuthenticatedClient,
    period: Union[
        Unset, GetUsageStatsOrganizationNameApiV1UsageStatsGetPeriod
    ] = GetUsageStatsOrganizationNameApiV1UsageStatsGetPeriod.MONTH,
    after: Union[None, Unset, datetime.datetime] = UNSET,
    before: Union[None, Unset, datetime.datetime] = UNSET,
) -> Optional[
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        UsageStatsResponse,
        ValidationErrorResponse,
    ]
]:
    """Get Usage Statistics

    Args:
        organization_name (str):
        period (Union[Unset, GetUsageStatsOrganizationNameApiV1UsageStatsGetPeriod]):  Default:
            GetUsageStatsOrganizationNameApiV1UsageStatsGetPeriod.MONTH.
        after (Union[None, Unset, datetime.datetime]):
        before (Union[None, Unset, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseErrorResponse, ChallengeResponse, UsageStatsResponse, ValidationErrorResponse]
    """

    return (
        await asyncio_detailed(
            organization_name=organization_name,
            client=client,
            period=period,
            after=after,
            before=before,
        )
    ).parsed

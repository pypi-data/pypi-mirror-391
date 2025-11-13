from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.base_error_response import BaseErrorResponse
from ...models.challenge_response import ChallengeResponse
from ...models.exec_response import ExecResponse
from ...models.try_rule_request import TryRuleRequest
from ...models.validation_error_response import ValidationErrorResponse
from ...types import Response


def _get_kwargs(
    organization_name: str,
    snapshot_uuid: UUID,
    *,
    body: TryRuleRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/{organization_name}/api/v1/snapshots/{snapshot_uuid}/try_rule".format(
            organization_name=organization_name,
            snapshot_uuid=snapshot_uuid,
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
    Union[BaseErrorResponse, ChallengeResponse, ExecResponse, ValidationErrorResponse]
]:
    if response.status_code == 200:
        response_200 = ExecResponse.from_dict(response.json())

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
    if response.status_code == 504:
        response_504 = BaseErrorResponse.from_dict(response.json())

        return response_504
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[BaseErrorResponse, ChallengeResponse, ExecResponse, ValidationErrorResponse]
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization_name: str,
    snapshot_uuid: UUID,
    *,
    client: AuthenticatedClient,
    body: TryRuleRequest,
) -> Response[
    Union[BaseErrorResponse, ChallengeResponse, ExecResponse, ValidationErrorResponse]
]:
    """Executes a single rule against the target snapshot.

    Args:
        organization_name (str):
        snapshot_uuid (UUID):
        body (TryRuleRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseErrorResponse, ChallengeResponse, ExecResponse, ValidationErrorResponse]]
    """

    kwargs = _get_kwargs(
        organization_name=organization_name,
        snapshot_uuid=snapshot_uuid,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_name: str,
    snapshot_uuid: UUID,
    *,
    client: AuthenticatedClient,
    body: TryRuleRequest,
) -> Optional[
    Union[BaseErrorResponse, ChallengeResponse, ExecResponse, ValidationErrorResponse]
]:
    """Executes a single rule against the target snapshot.

    Args:
        organization_name (str):
        snapshot_uuid (UUID):
        body (TryRuleRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseErrorResponse, ChallengeResponse, ExecResponse, ValidationErrorResponse]
    """

    return sync_detailed(
        organization_name=organization_name,
        snapshot_uuid=snapshot_uuid,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    organization_name: str,
    snapshot_uuid: UUID,
    *,
    client: AuthenticatedClient,
    body: TryRuleRequest,
) -> Response[
    Union[BaseErrorResponse, ChallengeResponse, ExecResponse, ValidationErrorResponse]
]:
    """Executes a single rule against the target snapshot.

    Args:
        organization_name (str):
        snapshot_uuid (UUID):
        body (TryRuleRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseErrorResponse, ChallengeResponse, ExecResponse, ValidationErrorResponse]]
    """

    kwargs = _get_kwargs(
        organization_name=organization_name,
        snapshot_uuid=snapshot_uuid,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_name: str,
    snapshot_uuid: UUID,
    *,
    client: AuthenticatedClient,
    body: TryRuleRequest,
) -> Optional[
    Union[BaseErrorResponse, ChallengeResponse, ExecResponse, ValidationErrorResponse]
]:
    """Executes a single rule against the target snapshot.

    Args:
        organization_name (str):
        snapshot_uuid (UUID):
        body (TryRuleRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseErrorResponse, ChallengeResponse, ExecResponse, ValidationErrorResponse]
    """

    return (
        await asyncio_detailed(
            organization_name=organization_name,
            snapshot_uuid=snapshot_uuid,
            client=client,
            body=body,
        )
    ).parsed

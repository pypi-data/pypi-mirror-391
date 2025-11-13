from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.base_error_response import BaseErrorResponse
from ...models.body_upload_snapshot_organization_name_api_v1_uploadsnapshot_post import (
    BodyUploadSnapshotOrganizationNameApiV1UploadsnapshotPost,
)
from ...models.challenge_response import ChallengeResponse
from ...models.upload_snapshot_response import UploadSnapshotResponse
from ...models.validation_error_response import ValidationErrorResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization_name: str,
    *,
    body: BodyUploadSnapshotOrganizationNameApiV1UploadsnapshotPost,
    network: Union[None, Unset, str] = UNSET,
    role: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    json_network: Union[None, Unset, str]
    if isinstance(network, Unset):
        json_network = UNSET
    else:
        json_network = network
    params["network"] = json_network

    json_role: Union[None, Unset, str]
    if isinstance(role, Unset):
        json_role = UNSET
    else:
        json_role = role
    params["role"] = json_role

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/{organization_name}/api/v1/uploadsnapshot/".format(
            organization_name=organization_name,
        ),
        "params": params,
    }

    _body = body.to_multipart()

    _kwargs["files"] = _body

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        Any,
        BaseErrorResponse,
        ChallengeResponse,
        UploadSnapshotResponse,
        ValidationErrorResponse,
    ]
]:
    if response.status_code == 200:
        response_200 = UploadSnapshotResponse.from_dict(response.json())

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
    if response.status_code == 413:
        response_413 = cast(Any, None)
        return response_413
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        Any,
        BaseErrorResponse,
        ChallengeResponse,
        UploadSnapshotResponse,
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
    body: BodyUploadSnapshotOrganizationNameApiV1UploadsnapshotPost,
    network: Union[None, Unset, str] = UNSET,
    role: Union[None, Unset, str] = UNSET,
) -> Response[
    Union[
        Any,
        BaseErrorResponse,
        ChallengeResponse,
        UploadSnapshotResponse,
        ValidationErrorResponse,
    ]
]:
    """Upload a snapshot

     Create a snapshot by direct upload. This triggers snapshot evaluation and rule processing.

    Args:
        organization_name (str):
        network (Union[None, Unset, str]):
        role (Union[None, Unset, str]):
        body (BodyUploadSnapshotOrganizationNameApiV1UploadsnapshotPost):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, BaseErrorResponse, ChallengeResponse, UploadSnapshotResponse, ValidationErrorResponse]]
    """

    kwargs = _get_kwargs(
        organization_name=organization_name,
        body=body,
        network=network,
        role=role,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_name: str,
    *,
    client: AuthenticatedClient,
    body: BodyUploadSnapshotOrganizationNameApiV1UploadsnapshotPost,
    network: Union[None, Unset, str] = UNSET,
    role: Union[None, Unset, str] = UNSET,
) -> Optional[
    Union[
        Any,
        BaseErrorResponse,
        ChallengeResponse,
        UploadSnapshotResponse,
        ValidationErrorResponse,
    ]
]:
    """Upload a snapshot

     Create a snapshot by direct upload. This triggers snapshot evaluation and rule processing.

    Args:
        organization_name (str):
        network (Union[None, Unset, str]):
        role (Union[None, Unset, str]):
        body (BodyUploadSnapshotOrganizationNameApiV1UploadsnapshotPost):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, BaseErrorResponse, ChallengeResponse, UploadSnapshotResponse, ValidationErrorResponse]
    """

    return sync_detailed(
        organization_name=organization_name,
        client=client,
        body=body,
        network=network,
        role=role,
    ).parsed


async def asyncio_detailed(
    organization_name: str,
    *,
    client: AuthenticatedClient,
    body: BodyUploadSnapshotOrganizationNameApiV1UploadsnapshotPost,
    network: Union[None, Unset, str] = UNSET,
    role: Union[None, Unset, str] = UNSET,
) -> Response[
    Union[
        Any,
        BaseErrorResponse,
        ChallengeResponse,
        UploadSnapshotResponse,
        ValidationErrorResponse,
    ]
]:
    """Upload a snapshot

     Create a snapshot by direct upload. This triggers snapshot evaluation and rule processing.

    Args:
        organization_name (str):
        network (Union[None, Unset, str]):
        role (Union[None, Unset, str]):
        body (BodyUploadSnapshotOrganizationNameApiV1UploadsnapshotPost):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, BaseErrorResponse, ChallengeResponse, UploadSnapshotResponse, ValidationErrorResponse]]
    """

    kwargs = _get_kwargs(
        organization_name=organization_name,
        body=body,
        network=network,
        role=role,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_name: str,
    *,
    client: AuthenticatedClient,
    body: BodyUploadSnapshotOrganizationNameApiV1UploadsnapshotPost,
    network: Union[None, Unset, str] = UNSET,
    role: Union[None, Unset, str] = UNSET,
) -> Optional[
    Union[
        Any,
        BaseErrorResponse,
        ChallengeResponse,
        UploadSnapshotResponse,
        ValidationErrorResponse,
    ]
]:
    """Upload a snapshot

     Create a snapshot by direct upload. This triggers snapshot evaluation and rule processing.

    Args:
        organization_name (str):
        network (Union[None, Unset, str]):
        role (Union[None, Unset, str]):
        body (BodyUploadSnapshotOrganizationNameApiV1UploadsnapshotPost):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, BaseErrorResponse, ChallengeResponse, UploadSnapshotResponse, ValidationErrorResponse]
    """

    return (
        await asyncio_detailed(
            organization_name=organization_name,
            client=client,
            body=body,
            network=network,
            role=role,
        )
    ).parsed

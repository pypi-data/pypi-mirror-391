from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.base_error_response import BaseErrorResponse
from ...models.challenge_response import ChallengeResponse
from ...models.update_editable_document_conflict_error_response import (
    UpdateEditableDocumentConflictErrorResponse,
)
from ...models.update_editable_document_request import UpdateEditableDocumentRequest
from ...models.validation_error_response import ValidationErrorResponse
from ...types import Response


def _get_kwargs(
    organization_name: str,
    document_uuid: UUID,
    *,
    body: UpdateEditableDocumentRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/{organization_name}/api/v1/edoc/{document_uuid}".format(
            organization_name=organization_name,
            document_uuid=document_uuid,
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
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        UpdateEditableDocumentConflictErrorResponse,
        ValidationErrorResponse,
    ]
]:
    if response.status_code == 422:
        response_422 = ValidationErrorResponse.from_dict(response.json())

        return response_422
    if response.status_code == 401:
        response_401 = ChallengeResponse.from_dict(response.json())

        return response_401
    if response.status_code == 404:
        response_404 = BaseErrorResponse.from_dict(response.json())

        return response_404
    if response.status_code == 412:
        response_412 = UpdateEditableDocumentConflictErrorResponse.from_dict(
            response.json()
        )

        return response_412
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
        UpdateEditableDocumentConflictErrorResponse,
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
    document_uuid: UUID,
    *,
    client: AuthenticatedClient,
    body: UpdateEditableDocumentRequest,
) -> Response[
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        UpdateEditableDocumentConflictErrorResponse,
        ValidationErrorResponse,
    ]
]:
    """Update Editable Document

    Args:
        organization_name (str):
        document_uuid (UUID):
        body (UpdateEditableDocumentRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseErrorResponse, ChallengeResponse, UpdateEditableDocumentConflictErrorResponse, ValidationErrorResponse]]
    """

    kwargs = _get_kwargs(
        organization_name=organization_name,
        document_uuid=document_uuid,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_name: str,
    document_uuid: UUID,
    *,
    client: AuthenticatedClient,
    body: UpdateEditableDocumentRequest,
) -> Optional[
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        UpdateEditableDocumentConflictErrorResponse,
        ValidationErrorResponse,
    ]
]:
    """Update Editable Document

    Args:
        organization_name (str):
        document_uuid (UUID):
        body (UpdateEditableDocumentRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseErrorResponse, ChallengeResponse, UpdateEditableDocumentConflictErrorResponse, ValidationErrorResponse]
    """

    return sync_detailed(
        organization_name=organization_name,
        document_uuid=document_uuid,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    organization_name: str,
    document_uuid: UUID,
    *,
    client: AuthenticatedClient,
    body: UpdateEditableDocumentRequest,
) -> Response[
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        UpdateEditableDocumentConflictErrorResponse,
        ValidationErrorResponse,
    ]
]:
    """Update Editable Document

    Args:
        organization_name (str):
        document_uuid (UUID):
        body (UpdateEditableDocumentRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseErrorResponse, ChallengeResponse, UpdateEditableDocumentConflictErrorResponse, ValidationErrorResponse]]
    """

    kwargs = _get_kwargs(
        organization_name=organization_name,
        document_uuid=document_uuid,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_name: str,
    document_uuid: UUID,
    *,
    client: AuthenticatedClient,
    body: UpdateEditableDocumentRequest,
) -> Optional[
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        UpdateEditableDocumentConflictErrorResponse,
        ValidationErrorResponse,
    ]
]:
    """Update Editable Document

    Args:
        organization_name (str):
        document_uuid (UUID):
        body (UpdateEditableDocumentRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseErrorResponse, ChallengeResponse, UpdateEditableDocumentConflictErrorResponse, ValidationErrorResponse]
    """

    return (
        await asyncio_detailed(
            organization_name=organization_name,
            document_uuid=document_uuid,
            client=client,
            body=body,
        )
    ).parsed

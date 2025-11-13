from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.base_error_response import BaseErrorResponse
from ...models.body_import_editable_document_organization_name_api_v1_edoc_import_post import (
    BodyImportEditableDocumentOrganizationNameApiV1EdocImportPost,
)
from ...models.challenge_response import ChallengeResponse
from ...models.document_type import DocumentType
from ...models.resource_type import ResourceType
from ...models.validation_error_response import ValidationErrorResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization_name: str,
    *,
    body: BodyImportEditableDocumentOrganizationNameApiV1EdocImportPost,
    resource_set_name: str,
    document_type: DocumentType,
    resource_type: ResourceType,
    file_path: Union[Unset, str] = "placeholder",
    description: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["resource_set_name"] = resource_set_name

    json_document_type = document_type.value
    params["document_type"] = json_document_type

    json_resource_type = resource_type.value
    params["resource_type"] = json_resource_type

    params["file_path"] = file_path

    json_description: Union[None, Unset, str]
    if isinstance(description, Unset):
        json_description = UNSET
    else:
        json_description = description
    params["description"] = json_description

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/{organization_name}/api/v1/edoc/import".format(
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
    *,
    client: AuthenticatedClient,
    body: BodyImportEditableDocumentOrganizationNameApiV1EdocImportPost,
    resource_set_name: str,
    document_type: DocumentType,
    resource_type: ResourceType,
    file_path: Union[Unset, str] = "placeholder",
    description: Union[None, Unset, str] = UNSET,
) -> Response[
    Union[Any, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]
]:
    """Import a file based policy for use in the web.

    Args:
        organization_name (str):
        resource_set_name (str):
        document_type (DocumentType):
        resource_type (ResourceType):
        file_path (Union[Unset, str]):  Default: 'placeholder'.
        description (Union[None, Unset, str]):
        body (BodyImportEditableDocumentOrganizationNameApiV1EdocImportPost):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]]
    """

    kwargs = _get_kwargs(
        organization_name=organization_name,
        body=body,
        resource_set_name=resource_set_name,
        document_type=document_type,
        resource_type=resource_type,
        file_path=file_path,
        description=description,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_name: str,
    *,
    client: AuthenticatedClient,
    body: BodyImportEditableDocumentOrganizationNameApiV1EdocImportPost,
    resource_set_name: str,
    document_type: DocumentType,
    resource_type: ResourceType,
    file_path: Union[Unset, str] = "placeholder",
    description: Union[None, Unset, str] = UNSET,
) -> Optional[
    Union[Any, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]
]:
    """Import a file based policy for use in the web.

    Args:
        organization_name (str):
        resource_set_name (str):
        document_type (DocumentType):
        resource_type (ResourceType):
        file_path (Union[Unset, str]):  Default: 'placeholder'.
        description (Union[None, Unset, str]):
        body (BodyImportEditableDocumentOrganizationNameApiV1EdocImportPost):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]
    """

    return sync_detailed(
        organization_name=organization_name,
        client=client,
        body=body,
        resource_set_name=resource_set_name,
        document_type=document_type,
        resource_type=resource_type,
        file_path=file_path,
        description=description,
    ).parsed


async def asyncio_detailed(
    organization_name: str,
    *,
    client: AuthenticatedClient,
    body: BodyImportEditableDocumentOrganizationNameApiV1EdocImportPost,
    resource_set_name: str,
    document_type: DocumentType,
    resource_type: ResourceType,
    file_path: Union[Unset, str] = "placeholder",
    description: Union[None, Unset, str] = UNSET,
) -> Response[
    Union[Any, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]
]:
    """Import a file based policy for use in the web.

    Args:
        organization_name (str):
        resource_set_name (str):
        document_type (DocumentType):
        resource_type (ResourceType):
        file_path (Union[Unset, str]):  Default: 'placeholder'.
        description (Union[None, Unset, str]):
        body (BodyImportEditableDocumentOrganizationNameApiV1EdocImportPost):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]]
    """

    kwargs = _get_kwargs(
        organization_name=organization_name,
        body=body,
        resource_set_name=resource_set_name,
        document_type=document_type,
        resource_type=resource_type,
        file_path=file_path,
        description=description,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_name: str,
    *,
    client: AuthenticatedClient,
    body: BodyImportEditableDocumentOrganizationNameApiV1EdocImportPost,
    resource_set_name: str,
    document_type: DocumentType,
    resource_type: ResourceType,
    file_path: Union[Unset, str] = "placeholder",
    description: Union[None, Unset, str] = UNSET,
) -> Optional[
    Union[Any, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]
]:
    """Import a file based policy for use in the web.

    Args:
        organization_name (str):
        resource_set_name (str):
        document_type (DocumentType):
        resource_type (ResourceType):
        file_path (Union[Unset, str]):  Default: 'placeholder'.
        description (Union[None, Unset, str]):
        body (BodyImportEditableDocumentOrganizationNameApiV1EdocImportPost):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, BaseErrorResponse, ChallengeResponse, ValidationErrorResponse]
    """

    return (
        await asyncio_detailed(
            organization_name=organization_name,
            client=client,
            body=body,
            resource_set_name=resource_set_name,
            document_type=document_type,
            resource_type=resource_type,
            file_path=file_path,
            description=description,
        )
    ).parsed

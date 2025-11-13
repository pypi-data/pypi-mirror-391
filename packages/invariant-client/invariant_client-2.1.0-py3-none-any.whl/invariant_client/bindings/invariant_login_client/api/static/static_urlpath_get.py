from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.validation_error_response import ValidationErrorResponse
from typing import Dict


def _get_kwargs(
    urlpath: str,
) -> Dict[str, Any]:
    return {
        "method": "get",
        "url": "/{urlpath}".format(
            urlpath=urlpath,
        ),
    }


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ValidationErrorResponse]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = response.json()
        return response_200
    if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        response_422 = ValidationErrorResponse.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, ValidationErrorResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    urlpath: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Any, ValidationErrorResponse]]:
    """Static files (catch-all)

    Args:
        urlpath (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ValidationErrorResponse]]
    """

    kwargs = _get_kwargs(
        urlpath=urlpath,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    urlpath: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Any, ValidationErrorResponse]]:
    """Static files (catch-all)

    Args:
        urlpath (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ValidationErrorResponse]
    """

    return sync_detailed(
        urlpath=urlpath,
        client=client,
    ).parsed


async def asyncio_detailed(
    urlpath: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Any, ValidationErrorResponse]]:
    """Static files (catch-all)

    Args:
        urlpath (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ValidationErrorResponse]]
    """

    kwargs = _get_kwargs(
        urlpath=urlpath,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    urlpath: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Any, ValidationErrorResponse]]:
    """Static files (catch-all)

    Args:
        urlpath (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ValidationErrorResponse]
    """

    return (
        await asyncio_detailed(
            urlpath=urlpath,
            client=client,
        )
    ).parsed

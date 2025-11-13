from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.base_error_response import BaseErrorResponse
from ...models.challenge_response import ChallengeResponse
from ...models.integration_with_status_github_installation import (
    IntegrationWithStatusGithubInstallation,
)
from ...models.integration_with_status_slack_app import IntegrationWithStatusSlackApp
from ...models.validation_error_response import ValidationErrorResponse
from ...types import Response


def _get_kwargs(
    organization_name: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/{organization_name}/api/v1/integrations/".format(
            organization_name=organization_name,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        BaseErrorResponse,
        ChallengeResponse,
        ValidationErrorResponse,
        list[
            Union[
                "IntegrationWithStatusGithubInstallation",
                "IntegrationWithStatusSlackApp",
            ]
        ],
    ]
]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:

            def _parse_response_200_item(
                data: object,
            ) -> Union[
                "IntegrationWithStatusGithubInstallation",
                "IntegrationWithStatusSlackApp",
            ]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    response_200_item_type_0 = (
                        IntegrationWithStatusGithubInstallation.from_dict(data)
                    )

                    return response_200_item_type_0
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                response_200_item_type_1 = IntegrationWithStatusSlackApp.from_dict(data)

                return response_200_item_type_1

            response_200_item = _parse_response_200_item(response_200_item_data)

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
        list[
            Union[
                "IntegrationWithStatusGithubInstallation",
                "IntegrationWithStatusSlackApp",
            ]
        ],
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
        BaseErrorResponse,
        ChallengeResponse,
        ValidationErrorResponse,
        list[
            Union[
                "IntegrationWithStatusGithubInstallation",
                "IntegrationWithStatusSlackApp",
            ]
        ],
    ]
]:
    """List integrations

    Args:
        organization_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseErrorResponse, ChallengeResponse, ValidationErrorResponse, list[Union['IntegrationWithStatusGithubInstallation', 'IntegrationWithStatusSlackApp']]]]
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
        BaseErrorResponse,
        ChallengeResponse,
        ValidationErrorResponse,
        list[
            Union[
                "IntegrationWithStatusGithubInstallation",
                "IntegrationWithStatusSlackApp",
            ]
        ],
    ]
]:
    """List integrations

    Args:
        organization_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseErrorResponse, ChallengeResponse, ValidationErrorResponse, list[Union['IntegrationWithStatusGithubInstallation', 'IntegrationWithStatusSlackApp']]]
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
        BaseErrorResponse,
        ChallengeResponse,
        ValidationErrorResponse,
        list[
            Union[
                "IntegrationWithStatusGithubInstallation",
                "IntegrationWithStatusSlackApp",
            ]
        ],
    ]
]:
    """List integrations

    Args:
        organization_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseErrorResponse, ChallengeResponse, ValidationErrorResponse, list[Union['IntegrationWithStatusGithubInstallation', 'IntegrationWithStatusSlackApp']]]]
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
        BaseErrorResponse,
        ChallengeResponse,
        ValidationErrorResponse,
        list[
            Union[
                "IntegrationWithStatusGithubInstallation",
                "IntegrationWithStatusSlackApp",
            ]
        ],
    ]
]:
    """List integrations

    Args:
        organization_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseErrorResponse, ChallengeResponse, ValidationErrorResponse, list[Union['IntegrationWithStatusGithubInstallation', 'IntegrationWithStatusSlackApp']]]
    """

    return (
        await asyncio_detailed(
            organization_name=organization_name,
            client=client,
        )
    ).parsed

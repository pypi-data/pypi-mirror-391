from http import HTTPStatus
from typing import Any, cast
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.deprecated_providers_response import DeprecatedProvidersResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    environment_id: None | Unset | UUID = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_environment_id: None | str | Unset
    if isinstance(environment_id, Unset):
        json_environment_id = UNSET
    elif isinstance(environment_id, UUID):
        json_environment_id = str(environment_id)
    else:
        json_environment_id = environment_id
    params["environment_id"] = json_environment_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/discovery/versions/deprecated",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | DeprecatedProvidersResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = DeprecatedProvidersResponse.from_dict(response.json())

        return response_200

    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | DeprecatedProvidersResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    environment_id: None | Unset | UUID = UNSET,
) -> Response[Any | DeprecatedProvidersResponse | HTTPValidationError]:
    """Get Deprecated Provider Configs

     Get all provider instances using deprecated config versions.

    Args:
        environment_id (None | Unset | UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | DeprecatedProvidersResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        environment_id=environment_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    environment_id: None | Unset | UUID = UNSET,
) -> Any | DeprecatedProvidersResponse | HTTPValidationError | None:
    """Get Deprecated Provider Configs

     Get all provider instances using deprecated config versions.

    Args:
        environment_id (None | Unset | UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | DeprecatedProvidersResponse | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        environment_id=environment_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    environment_id: None | Unset | UUID = UNSET,
) -> Response[Any | DeprecatedProvidersResponse | HTTPValidationError]:
    """Get Deprecated Provider Configs

     Get all provider instances using deprecated config versions.

    Args:
        environment_id (None | Unset | UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | DeprecatedProvidersResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        environment_id=environment_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    environment_id: None | Unset | UUID = UNSET,
) -> Any | DeprecatedProvidersResponse | HTTPValidationError | None:
    """Get Deprecated Provider Configs

     Get all provider instances using deprecated config versions.

    Args:
        environment_id (None | Unset | UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | DeprecatedProvidersResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            environment_id=environment_id,
        )
    ).parsed

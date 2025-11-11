from http import HTTPStatus
from typing import Any, cast
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.configured_provider_response import ConfiguredProviderResponse
from ...models.configured_provider_update import ConfiguredProviderUpdate
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    provider_id: UUID,
    *,
    body: ConfiguredProviderUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/api/v1/discovery/configured-providers/{provider_id}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | ConfiguredProviderResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = ConfiguredProviderResponse.from_dict(response.json())

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
) -> Response[Any | ConfiguredProviderResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    provider_id: UUID,
    *,
    client: AuthenticatedClient,
    body: ConfiguredProviderUpdate,
) -> Response[Any | ConfiguredProviderResponse | HTTPValidationError]:
    """Update Configured Provider

     Update a configured discovery provider.

    Only provided fields will be updated. To update secrets, provide the full
    config object with new secret values.

    Args:
        provider_id (UUID):
        body (ConfiguredProviderUpdate): Request to update a configured discovery provider.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ConfiguredProviderResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        provider_id=provider_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    provider_id: UUID,
    *,
    client: AuthenticatedClient,
    body: ConfiguredProviderUpdate,
) -> Any | ConfiguredProviderResponse | HTTPValidationError | None:
    """Update Configured Provider

     Update a configured discovery provider.

    Only provided fields will be updated. To update secrets, provide the full
    config object with new secret values.

    Args:
        provider_id (UUID):
        body (ConfiguredProviderUpdate): Request to update a configured discovery provider.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ConfiguredProviderResponse | HTTPValidationError
    """

    return sync_detailed(
        provider_id=provider_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    provider_id: UUID,
    *,
    client: AuthenticatedClient,
    body: ConfiguredProviderUpdate,
) -> Response[Any | ConfiguredProviderResponse | HTTPValidationError]:
    """Update Configured Provider

     Update a configured discovery provider.

    Only provided fields will be updated. To update secrets, provide the full
    config object with new secret values.

    Args:
        provider_id (UUID):
        body (ConfiguredProviderUpdate): Request to update a configured discovery provider.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ConfiguredProviderResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        provider_id=provider_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    provider_id: UUID,
    *,
    client: AuthenticatedClient,
    body: ConfiguredProviderUpdate,
) -> Any | ConfiguredProviderResponse | HTTPValidationError | None:
    """Update Configured Provider

     Update a configured discovery provider.

    Only provided fields will be updated. To update secrets, provide the full
    config object with new secret values.

    Args:
        provider_id (UUID):
        body (ConfiguredProviderUpdate): Request to update a configured discovery provider.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ConfiguredProviderResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            provider_id=provider_id,
            client=client,
            body=body,
        )
    ).parsed

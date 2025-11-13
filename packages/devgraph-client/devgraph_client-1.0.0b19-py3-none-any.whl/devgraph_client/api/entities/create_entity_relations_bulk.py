from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.bulk_entity_relation_create_request import BulkEntityRelationCreateRequest
from ...models.bulk_entity_relation_response import BulkEntityRelationResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    *,
    body: BulkEntityRelationCreateRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/entities/relations/bulk",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | BulkEntityRelationResponse | HTTPValidationError | None:
    if response.status_code == 201:
        response_201 = BulkEntityRelationResponse.from_dict(response.json())

        return response_201

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
) -> Response[Any | BulkEntityRelationResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: BulkEntityRelationCreateRequest,
) -> Response[Any | BulkEntityRelationResponse | HTTPValidationError]:
    """Create multiple entity relations in bulk

     Creates multiple entity relations in a single request. Provides detailed success/failure information
    for each relation. Requires 'create:entityrelations' permission.

    Args:
        body (BulkEntityRelationCreateRequest): Request model for creating multiple entity
            relations in bulk.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | BulkEntityRelationResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: BulkEntityRelationCreateRequest,
) -> Any | BulkEntityRelationResponse | HTTPValidationError | None:
    """Create multiple entity relations in bulk

     Creates multiple entity relations in a single request. Provides detailed success/failure information
    for each relation. Requires 'create:entityrelations' permission.

    Args:
        body (BulkEntityRelationCreateRequest): Request model for creating multiple entity
            relations in bulk.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | BulkEntityRelationResponse | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: BulkEntityRelationCreateRequest,
) -> Response[Any | BulkEntityRelationResponse | HTTPValidationError]:
    """Create multiple entity relations in bulk

     Creates multiple entity relations in a single request. Provides detailed success/failure information
    for each relation. Requires 'create:entityrelations' permission.

    Args:
        body (BulkEntityRelationCreateRequest): Request model for creating multiple entity
            relations in bulk.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | BulkEntityRelationResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: BulkEntityRelationCreateRequest,
) -> Any | BulkEntityRelationResponse | HTTPValidationError | None:
    """Create multiple entity relations in bulk

     Creates multiple entity relations in a single request. Provides detailed success/failure information
    for each relation. Requires 'create:entityrelations' permission.

    Args:
        body (BulkEntityRelationCreateRequest): Request model for creating multiple entity
            relations in bulk.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | BulkEntityRelationResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed

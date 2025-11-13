from http import HTTPStatus
from typing import Any, cast
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.mcp_endpoint_response import MCPEndpointResponse
from ...models.mcp_endpoint_update import MCPEndpointUpdate
from ...types import Response


def _get_kwargs(
    mcpendpoint_id: UUID,
    *,
    body: MCPEndpointUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/api/v1/mcp/endpoints/{mcpendpoint_id}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | HTTPValidationError | MCPEndpointResponse | None:
    if response.status_code == 200:
        response_200 = MCPEndpointResponse.from_dict(response.json())

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
) -> Response[Any | HTTPValidationError | MCPEndpointResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    mcpendpoint_id: UUID,
    *,
    client: AuthenticatedClient,
    body: MCPEndpointUpdate,
) -> Response[Any | HTTPValidationError | MCPEndpointResponse]:
    """Update Mcpendpoint

     Update a specific MCP endpoint configuration by ID

    Args:
        mcpendpoint_id (UUID):
        body (MCPEndpointUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | MCPEndpointResponse]
    """

    kwargs = _get_kwargs(
        mcpendpoint_id=mcpendpoint_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    mcpendpoint_id: UUID,
    *,
    client: AuthenticatedClient,
    body: MCPEndpointUpdate,
) -> Any | HTTPValidationError | MCPEndpointResponse | None:
    """Update Mcpendpoint

     Update a specific MCP endpoint configuration by ID

    Args:
        mcpendpoint_id (UUID):
        body (MCPEndpointUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | MCPEndpointResponse
    """

    return sync_detailed(
        mcpendpoint_id=mcpendpoint_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    mcpendpoint_id: UUID,
    *,
    client: AuthenticatedClient,
    body: MCPEndpointUpdate,
) -> Response[Any | HTTPValidationError | MCPEndpointResponse]:
    """Update Mcpendpoint

     Update a specific MCP endpoint configuration by ID

    Args:
        mcpendpoint_id (UUID):
        body (MCPEndpointUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | MCPEndpointResponse]
    """

    kwargs = _get_kwargs(
        mcpendpoint_id=mcpendpoint_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    mcpendpoint_id: UUID,
    *,
    client: AuthenticatedClient,
    body: MCPEndpointUpdate,
) -> Any | HTTPValidationError | MCPEndpointResponse | None:
    """Update Mcpendpoint

     Update a specific MCP endpoint configuration by ID

    Args:
        mcpendpoint_id (UUID):
        body (MCPEndpointUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | MCPEndpointResponse
    """

    return (
        await asyncio_detailed(
            mcpendpoint_id=mcpendpoint_id,
            client=client,
            body=body,
        )
    ).parsed

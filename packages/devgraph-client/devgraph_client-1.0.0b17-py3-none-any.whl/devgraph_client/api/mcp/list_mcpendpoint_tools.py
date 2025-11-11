from http import HTTPStatus
from typing import Any, cast
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.list_mcpendpoint_tools_response_200_item import ListMcpendpointToolsResponse200Item
from ...types import Response


def _get_kwargs(
    mcpendpoint_id: UUID,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/mcp/endpoints/{mcpendpoint_id}/tools",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | HTTPValidationError | list[ListMcpendpointToolsResponse200Item] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ListMcpendpointToolsResponse200Item.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[Any | HTTPValidationError | list[ListMcpendpointToolsResponse200Item]]:
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
) -> Response[Any | HTTPValidationError | list[ListMcpendpointToolsResponse200Item]]:
    """List Mcpendpoint Tools

     List all available tools from a specific MCP endpoint

    Args:
        mcpendpoint_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | list[ListMcpendpointToolsResponse200Item]]
    """

    kwargs = _get_kwargs(
        mcpendpoint_id=mcpendpoint_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    mcpendpoint_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Any | HTTPValidationError | list[ListMcpendpointToolsResponse200Item] | None:
    """List Mcpendpoint Tools

     List all available tools from a specific MCP endpoint

    Args:
        mcpendpoint_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | list[ListMcpendpointToolsResponse200Item]
    """

    return sync_detailed(
        mcpendpoint_id=mcpendpoint_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    mcpendpoint_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[Any | HTTPValidationError | list[ListMcpendpointToolsResponse200Item]]:
    """List Mcpendpoint Tools

     List all available tools from a specific MCP endpoint

    Args:
        mcpendpoint_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | list[ListMcpendpointToolsResponse200Item]]
    """

    kwargs = _get_kwargs(
        mcpendpoint_id=mcpendpoint_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    mcpendpoint_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Any | HTTPValidationError | list[ListMcpendpointToolsResponse200Item] | None:
    """List Mcpendpoint Tools

     List all available tools from a specific MCP endpoint

    Args:
        mcpendpoint_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | list[ListMcpendpointToolsResponse200Item]
    """

    return (
        await asyncio_detailed(
            mcpendpoint_id=mcpendpoint_id,
            client=client,
        )
    ).parsed

from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.mcp_tool_entity_association_response import MCPToolEntityAssociationResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    mcpendpoint_name: str,
    *,
    tool_name: None | str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_tool_name: None | str | Unset
    if isinstance(tool_name, Unset):
        json_tool_name = UNSET
    else:
        json_tool_name = tool_name
    params["tool_name"] = json_tool_name

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/mcp/endpoints/{mcpendpoint_name}/entity-types",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | HTTPValidationError | list[MCPToolEntityAssociationResponse] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = MCPToolEntityAssociationResponse.from_dict(response_200_item_data)

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
) -> Response[Any | HTTPValidationError | list[MCPToolEntityAssociationResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    mcpendpoint_name: str,
    *,
    client: AuthenticatedClient,
    tool_name: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError | list[MCPToolEntityAssociationResponse]]:
    """Get Mcp Endpoint Entity Types

     Get all entity types associated with an MCP endpoint's tools

    Args:
        mcpendpoint_name (str):
        tool_name (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | list[MCPToolEntityAssociationResponse]]
    """

    kwargs = _get_kwargs(
        mcpendpoint_name=mcpendpoint_name,
        tool_name=tool_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    mcpendpoint_name: str,
    *,
    client: AuthenticatedClient,
    tool_name: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | list[MCPToolEntityAssociationResponse] | None:
    """Get Mcp Endpoint Entity Types

     Get all entity types associated with an MCP endpoint's tools

    Args:
        mcpendpoint_name (str):
        tool_name (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | list[MCPToolEntityAssociationResponse]
    """

    return sync_detailed(
        mcpendpoint_name=mcpendpoint_name,
        client=client,
        tool_name=tool_name,
    ).parsed


async def asyncio_detailed(
    mcpendpoint_name: str,
    *,
    client: AuthenticatedClient,
    tool_name: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError | list[MCPToolEntityAssociationResponse]]:
    """Get Mcp Endpoint Entity Types

     Get all entity types associated with an MCP endpoint's tools

    Args:
        mcpendpoint_name (str):
        tool_name (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | list[MCPToolEntityAssociationResponse]]
    """

    kwargs = _get_kwargs(
        mcpendpoint_name=mcpendpoint_name,
        tool_name=tool_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    mcpendpoint_name: str,
    *,
    client: AuthenticatedClient,
    tool_name: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | list[MCPToolEntityAssociationResponse] | None:
    """Get Mcp Endpoint Entity Types

     Get all entity types associated with an MCP endpoint's tools

    Args:
        mcpendpoint_name (str):
        tool_name (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | list[MCPToolEntityAssociationResponse]
    """

    return (
        await asyncio_detailed(
            mcpendpoint_name=mcpendpoint_name,
            client=client,
            tool_name=tool_name,
        )
    ).parsed

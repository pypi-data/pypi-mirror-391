from http import HTTPStatus
from typing import Any, cast
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.mcp_tool_entity_association_response import MCPToolEntityAssociationResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    entity_definition_id: UUID,
    *,
    entity_version_id: None | Unset | UUID = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_entity_version_id: None | str | Unset
    if isinstance(entity_version_id, Unset):
        json_entity_version_id = UNSET
    elif isinstance(entity_version_id, UUID):
        json_entity_version_id = str(entity_version_id)
    else:
        json_entity_version_id = entity_version_id
    params["entity_version_id"] = json_entity_version_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/mcp/entity-definitions/{entity_definition_id}/tools",
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
    entity_definition_id: UUID,
    *,
    client: AuthenticatedClient,
    entity_version_id: None | Unset | UUID = UNSET,
) -> Response[Any | HTTPValidationError | list[MCPToolEntityAssociationResponse]]:
    """Get Entity Tools

     Get all MCP tools associated with an entity definition

    Args:
        entity_definition_id (UUID):
        entity_version_id (None | Unset | UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | list[MCPToolEntityAssociationResponse]]
    """

    kwargs = _get_kwargs(
        entity_definition_id=entity_definition_id,
        entity_version_id=entity_version_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    entity_definition_id: UUID,
    *,
    client: AuthenticatedClient,
    entity_version_id: None | Unset | UUID = UNSET,
) -> Any | HTTPValidationError | list[MCPToolEntityAssociationResponse] | None:
    """Get Entity Tools

     Get all MCP tools associated with an entity definition

    Args:
        entity_definition_id (UUID):
        entity_version_id (None | Unset | UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | list[MCPToolEntityAssociationResponse]
    """

    return sync_detailed(
        entity_definition_id=entity_definition_id,
        client=client,
        entity_version_id=entity_version_id,
    ).parsed


async def asyncio_detailed(
    entity_definition_id: UUID,
    *,
    client: AuthenticatedClient,
    entity_version_id: None | Unset | UUID = UNSET,
) -> Response[Any | HTTPValidationError | list[MCPToolEntityAssociationResponse]]:
    """Get Entity Tools

     Get all MCP tools associated with an entity definition

    Args:
        entity_definition_id (UUID):
        entity_version_id (None | Unset | UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | list[MCPToolEntityAssociationResponse]]
    """

    kwargs = _get_kwargs(
        entity_definition_id=entity_definition_id,
        entity_version_id=entity_version_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    entity_definition_id: UUID,
    *,
    client: AuthenticatedClient,
    entity_version_id: None | Unset | UUID = UNSET,
) -> Any | HTTPValidationError | list[MCPToolEntityAssociationResponse] | None:
    """Get Entity Tools

     Get all MCP tools associated with an entity definition

    Args:
        entity_definition_id (UUID):
        entity_version_id (None | Unset | UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | list[MCPToolEntityAssociationResponse]
    """

    return (
        await asyncio_detailed(
            entity_definition_id=entity_definition_id,
            client=client,
            entity_version_id=entity_version_id,
        )
    ).parsed

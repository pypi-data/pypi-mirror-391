from http import HTTPStatus
from typing import Any, cast
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    definition_id: UUID,
    *,
    mark_orphans_only: bool | Unset = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["mark_orphans_only"] = mark_orphans_only

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/api/v1/entities/definitions/{definition_id}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | HTTPValidationError | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204

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
) -> Response[Any | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    definition_id: UUID,
    *,
    client: AuthenticatedClient,
    mark_orphans_only: bool | Unset = False,
) -> Response[Any | HTTPValidationError]:
    """Delete an entity definition

     Delete an entity definition, all its versions, and optionally mark associated entities as orphans

    Args:
        definition_id (UUID):
        mark_orphans_only (bool | Unset): If true, mark entities as orphans instead of deleting
            them immediately Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        definition_id=definition_id,
        mark_orphans_only=mark_orphans_only,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    definition_id: UUID,
    *,
    client: AuthenticatedClient,
    mark_orphans_only: bool | Unset = False,
) -> Any | HTTPValidationError | None:
    """Delete an entity definition

     Delete an entity definition, all its versions, and optionally mark associated entities as orphans

    Args:
        definition_id (UUID):
        mark_orphans_only (bool | Unset): If true, mark entities as orphans instead of deleting
            them immediately Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        definition_id=definition_id,
        client=client,
        mark_orphans_only=mark_orphans_only,
    ).parsed


async def asyncio_detailed(
    definition_id: UUID,
    *,
    client: AuthenticatedClient,
    mark_orphans_only: bool | Unset = False,
) -> Response[Any | HTTPValidationError]:
    """Delete an entity definition

     Delete an entity definition, all its versions, and optionally mark associated entities as orphans

    Args:
        definition_id (UUID):
        mark_orphans_only (bool | Unset): If true, mark entities as orphans instead of deleting
            them immediately Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        definition_id=definition_id,
        mark_orphans_only=mark_orphans_only,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    definition_id: UUID,
    *,
    client: AuthenticatedClient,
    mark_orphans_only: bool | Unset = False,
) -> Any | HTTPValidationError | None:
    """Delete an entity definition

     Delete an entity definition, all its versions, and optionally mark associated entities as orphans

    Args:
        definition_id (UUID):
        mark_orphans_only (bool | Unset): If true, mark entities as orphans instead of deleting
            them immediately Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            definition_id=definition_id,
            client=client,
            mark_orphans_only=mark_orphans_only,
        )
    ).parsed

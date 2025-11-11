from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.entity_result_set_response import EntityResultSetResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    name: str | Unset = UNSET,
    label: str | Unset = UNSET,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
    include_relations: bool | Unset = True,
    field_selector: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["name"] = name

    params["label"] = label

    params["limit"] = limit

    params["offset"] = offset

    params["include_relations"] = include_relations

    params["fieldSelector"] = field_selector

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/entities/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | EntityResultSetResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = EntityResultSetResponse.from_dict(response.json())

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
) -> Response[Any | EntityResultSetResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    name: str | Unset = UNSET,
    label: str | Unset = UNSET,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
    include_relations: bool | Unset = True,
    field_selector: str | Unset = UNSET,
) -> Response[Any | EntityResultSetResponse | HTTPValidationError]:
    """Query entities with optional field selectors

     Retrieves entities from the ontology, optionally filtered by field selectors. Field selectors use
    dot notation for nested properties (e.g., 'spec.metadata.owner=team-a'). Requires 'read:entities'
    permission.

    Args:
        name (str | Unset):
        label (str | Unset):
        limit (int | Unset):  Default: 100.
        offset (int | Unset):  Default: 0.
        include_relations (bool | Unset): Include relations in the response. Set to false for
            faster queries when relations are not needed. Default: True.
        field_selector (str | Unset): Comma-separated field selectors in format 'key=value',
            supports dot notation for nested properties

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | EntityResultSetResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        name=name,
        label=label,
        limit=limit,
        offset=offset,
        include_relations=include_relations,
        field_selector=field_selector,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    name: str | Unset = UNSET,
    label: str | Unset = UNSET,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
    include_relations: bool | Unset = True,
    field_selector: str | Unset = UNSET,
) -> Any | EntityResultSetResponse | HTTPValidationError | None:
    """Query entities with optional field selectors

     Retrieves entities from the ontology, optionally filtered by field selectors. Field selectors use
    dot notation for nested properties (e.g., 'spec.metadata.owner=team-a'). Requires 'read:entities'
    permission.

    Args:
        name (str | Unset):
        label (str | Unset):
        limit (int | Unset):  Default: 100.
        offset (int | Unset):  Default: 0.
        include_relations (bool | Unset): Include relations in the response. Set to false for
            faster queries when relations are not needed. Default: True.
        field_selector (str | Unset): Comma-separated field selectors in format 'key=value',
            supports dot notation for nested properties

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | EntityResultSetResponse | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        name=name,
        label=label,
        limit=limit,
        offset=offset,
        include_relations=include_relations,
        field_selector=field_selector,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    name: str | Unset = UNSET,
    label: str | Unset = UNSET,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
    include_relations: bool | Unset = True,
    field_selector: str | Unset = UNSET,
) -> Response[Any | EntityResultSetResponse | HTTPValidationError]:
    """Query entities with optional field selectors

     Retrieves entities from the ontology, optionally filtered by field selectors. Field selectors use
    dot notation for nested properties (e.g., 'spec.metadata.owner=team-a'). Requires 'read:entities'
    permission.

    Args:
        name (str | Unset):
        label (str | Unset):
        limit (int | Unset):  Default: 100.
        offset (int | Unset):  Default: 0.
        include_relations (bool | Unset): Include relations in the response. Set to false for
            faster queries when relations are not needed. Default: True.
        field_selector (str | Unset): Comma-separated field selectors in format 'key=value',
            supports dot notation for nested properties

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | EntityResultSetResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        name=name,
        label=label,
        limit=limit,
        offset=offset,
        include_relations=include_relations,
        field_selector=field_selector,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    name: str | Unset = UNSET,
    label: str | Unset = UNSET,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
    include_relations: bool | Unset = True,
    field_selector: str | Unset = UNSET,
) -> Any | EntityResultSetResponse | HTTPValidationError | None:
    """Query entities with optional field selectors

     Retrieves entities from the ontology, optionally filtered by field selectors. Field selectors use
    dot notation for nested properties (e.g., 'spec.metadata.owner=team-a'). Requires 'read:entities'
    permission.

    Args:
        name (str | Unset):
        label (str | Unset):
        limit (int | Unset):  Default: 100.
        offset (int | Unset):  Default: 0.
        include_relations (bool | Unset): Include relations in the response. Set to false for
            faster queries when relations are not needed. Default: True.
        field_selector (str | Unset): Comma-separated field selectors in format 'key=value',
            supports dot notation for nested properties

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | EntityResultSetResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            name=name,
            label=label,
            limit=limit,
            offset=offset,
            include_relations=include_relations,
            field_selector=field_selector,
        )
    ).parsed

from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_entities_bulk_response_create_entities_bulk import CreateEntitiesBulkResponseCreateEntitiesBulk
from ...models.entity import Entity
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response


def _get_kwargs(
    *,
    body: list[Entity],
    group: str,
    version: str,
    namespace: str,
    plural: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["group"] = group

    params["version"] = version

    params["namespace"] = namespace

    params["plural"] = plural

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/entities/bulk",
        "params": params,
    }

    _kwargs["json"] = []
    for body_item_data in body:
        body_item = body_item_data.to_dict()
        _kwargs["json"].append(body_item)

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | CreateEntitiesBulkResponseCreateEntitiesBulk | HTTPValidationError | None:
    if response.status_code == 201:
        response_201 = CreateEntitiesBulkResponseCreateEntitiesBulk.from_dict(response.json())

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
) -> Response[Any | CreateEntitiesBulkResponseCreateEntitiesBulk | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: list[Entity],
    group: str,
    version: str,
    namespace: str,
    plural: str,
) -> Response[Any | CreateEntitiesBulkResponseCreateEntitiesBulk | HTTPValidationError]:
    """Create multiple entities in bulk

     Creates multiple entities in a single request with concurrent processing. Provides detailed
    success/failure information for each entity. Requires 'create:entities' permission.

    Args:
        group (str):
        version (str):
        namespace (str):
        plural (str):
        body (list[Entity]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | CreateEntitiesBulkResponseCreateEntitiesBulk | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
        group=group,
        version=version,
        namespace=namespace,
        plural=plural,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: list[Entity],
    group: str,
    version: str,
    namespace: str,
    plural: str,
) -> Any | CreateEntitiesBulkResponseCreateEntitiesBulk | HTTPValidationError | None:
    """Create multiple entities in bulk

     Creates multiple entities in a single request with concurrent processing. Provides detailed
    success/failure information for each entity. Requires 'create:entities' permission.

    Args:
        group (str):
        version (str):
        namespace (str):
        plural (str):
        body (list[Entity]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | CreateEntitiesBulkResponseCreateEntitiesBulk | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        body=body,
        group=group,
        version=version,
        namespace=namespace,
        plural=plural,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: list[Entity],
    group: str,
    version: str,
    namespace: str,
    plural: str,
) -> Response[Any | CreateEntitiesBulkResponseCreateEntitiesBulk | HTTPValidationError]:
    """Create multiple entities in bulk

     Creates multiple entities in a single request with concurrent processing. Provides detailed
    success/failure information for each entity. Requires 'create:entities' permission.

    Args:
        group (str):
        version (str):
        namespace (str):
        plural (str):
        body (list[Entity]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | CreateEntitiesBulkResponseCreateEntitiesBulk | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
        group=group,
        version=version,
        namespace=namespace,
        plural=plural,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: list[Entity],
    group: str,
    version: str,
    namespace: str,
    plural: str,
) -> Any | CreateEntitiesBulkResponseCreateEntitiesBulk | HTTPValidationError | None:
    """Create multiple entities in bulk

     Creates multiple entities in a single request with concurrent processing. Provides detailed
    success/failure information for each entity. Requires 'create:entities' permission.

    Args:
        group (str):
        version (str):
        namespace (str):
        plural (str):
        body (list[Entity]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | CreateEntitiesBulkResponseCreateEntitiesBulk | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            group=group,
            version=version,
            namespace=namespace,
            plural=plural,
        )
    ).parsed

from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.entity import Entity
from ...models.entity_response import EntityResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    group: str,
    version: str,
    namespace: str,
    plural: str,
    *,
    body: Entity,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v1/entities/{group}/{version}/namespace/{namespace}/{plural}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | EntityResponse | HTTPValidationError | None:
    if response.status_code == 201:
        response_201 = EntityResponse.from_dict(response.json())

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
) -> Response[Any | EntityResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    group: str,
    version: str,
    namespace: str,
    plural: str,
    *,
    client: AuthenticatedClient,
    body: Entity,
) -> Response[Any | EntityResponse | HTTPValidationError]:
    """Create a resource based on an entity definition

     Creates a new entity based on the specified group, version, namespace, and kind. Requires
    'create:entities' permission.

    Args:
        group (str):
        version (str):
        namespace (str):
        plural (str):
        body (Entity):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | EntityResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        group=group,
        version=version,
        namespace=namespace,
        plural=plural,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    group: str,
    version: str,
    namespace: str,
    plural: str,
    *,
    client: AuthenticatedClient,
    body: Entity,
) -> Any | EntityResponse | HTTPValidationError | None:
    """Create a resource based on an entity definition

     Creates a new entity based on the specified group, version, namespace, and kind. Requires
    'create:entities' permission.

    Args:
        group (str):
        version (str):
        namespace (str):
        plural (str):
        body (Entity):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | EntityResponse | HTTPValidationError
    """

    return sync_detailed(
        group=group,
        version=version,
        namespace=namespace,
        plural=plural,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    group: str,
    version: str,
    namespace: str,
    plural: str,
    *,
    client: AuthenticatedClient,
    body: Entity,
) -> Response[Any | EntityResponse | HTTPValidationError]:
    """Create a resource based on an entity definition

     Creates a new entity based on the specified group, version, namespace, and kind. Requires
    'create:entities' permission.

    Args:
        group (str):
        version (str):
        namespace (str):
        plural (str):
        body (Entity):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | EntityResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        group=group,
        version=version,
        namespace=namespace,
        plural=plural,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    group: str,
    version: str,
    namespace: str,
    plural: str,
    *,
    client: AuthenticatedClient,
    body: Entity,
) -> Any | EntityResponse | HTTPValidationError | None:
    """Create a resource based on an entity definition

     Creates a new entity based on the specified group, version, namespace, and kind. Requires
    'create:entities' permission.

    Args:
        group (str):
        version (str):
        namespace (str):
        plural (str):
        body (Entity):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | EntityResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            group=group,
            version=version,
            namespace=namespace,
            plural=plural,
            client=client,
            body=body,
        )
    ).parsed

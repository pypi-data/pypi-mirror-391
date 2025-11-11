from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.entity_with_relations_response import EntityWithRelationsResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    uid: str,
    *,
    namespace: str | Unset = "default",
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["namespace"] = namespace

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/entities/uid/{uid}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | EntityWithRelationsResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = EntityWithRelationsResponse.from_dict(response.json())

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
) -> Response[Any | EntityWithRelationsResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    uid: str,
    *,
    client: AuthenticatedClient,
    namespace: str | Unset = "default",
) -> Response[Any | EntityWithRelationsResponse | HTTPValidationError]:
    """Retrieve a specific entity by UID with its relations

     Fetches a specific entity by its unique identifier (UID), including related entities and relations.
    Requires 'read:entities' permission.

    Args:
        uid (str):
        namespace (str | Unset):  Default: 'default'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | EntityWithRelationsResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        uid=uid,
        namespace=namespace,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    uid: str,
    *,
    client: AuthenticatedClient,
    namespace: str | Unset = "default",
) -> Any | EntityWithRelationsResponse | HTTPValidationError | None:
    """Retrieve a specific entity by UID with its relations

     Fetches a specific entity by its unique identifier (UID), including related entities and relations.
    Requires 'read:entities' permission.

    Args:
        uid (str):
        namespace (str | Unset):  Default: 'default'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | EntityWithRelationsResponse | HTTPValidationError
    """

    return sync_detailed(
        uid=uid,
        client=client,
        namespace=namespace,
    ).parsed


async def asyncio_detailed(
    uid: str,
    *,
    client: AuthenticatedClient,
    namespace: str | Unset = "default",
) -> Response[Any | EntityWithRelationsResponse | HTTPValidationError]:
    """Retrieve a specific entity by UID with its relations

     Fetches a specific entity by its unique identifier (UID), including related entities and relations.
    Requires 'read:entities' permission.

    Args:
        uid (str):
        namespace (str | Unset):  Default: 'default'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | EntityWithRelationsResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        uid=uid,
        namespace=namespace,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    uid: str,
    *,
    client: AuthenticatedClient,
    namespace: str | Unset = "default",
) -> Any | EntityWithRelationsResponse | HTTPValidationError | None:
    """Retrieve a specific entity by UID with its relations

     Fetches a specific entity by its unique identifier (UID), including related entities and relations.
    Requires 'read:entities' permission.

    Args:
        uid (str):
        namespace (str | Unset):  Default: 'default'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | EntityWithRelationsResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            uid=uid,
            client=client,
            namespace=namespace,
        )
    ).parsed

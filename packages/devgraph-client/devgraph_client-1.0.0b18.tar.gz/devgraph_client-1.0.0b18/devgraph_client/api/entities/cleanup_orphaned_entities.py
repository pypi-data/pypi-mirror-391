from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    namespace: str | Unset = "default",
    max_age_hours: int | Unset = 24,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["namespace"] = namespace

    params["max_age_hours"] = max_age_hours

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/api/v1/entities/orphans",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = response.json()
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
) -> Response[Any | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    namespace: str | Unset = "default",
    max_age_hours: int | Unset = 24,
) -> Response[Any | HTTPValidationError]:
    """Clean up orphaned entities

     Delete all entities marked as orphans. Requires 'delete:entities' permission.

    Args:
        namespace (str | Unset): Namespace to clean up (default: 'default') Default: 'default'.
        max_age_hours (int | Unset): Only delete orphans older than this many hours Default: 24.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        namespace=namespace,
        max_age_hours=max_age_hours,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    namespace: str | Unset = "default",
    max_age_hours: int | Unset = 24,
) -> Any | HTTPValidationError | None:
    """Clean up orphaned entities

     Delete all entities marked as orphans. Requires 'delete:entities' permission.

    Args:
        namespace (str | Unset): Namespace to clean up (default: 'default') Default: 'default'.
        max_age_hours (int | Unset): Only delete orphans older than this many hours Default: 24.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        namespace=namespace,
        max_age_hours=max_age_hours,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    namespace: str | Unset = "default",
    max_age_hours: int | Unset = 24,
) -> Response[Any | HTTPValidationError]:
    """Clean up orphaned entities

     Delete all entities marked as orphans. Requires 'delete:entities' permission.

    Args:
        namespace (str | Unset): Namespace to clean up (default: 'default') Default: 'default'.
        max_age_hours (int | Unset): Only delete orphans older than this many hours Default: 24.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        namespace=namespace,
        max_age_hours=max_age_hours,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    namespace: str | Unset = "default",
    max_age_hours: int | Unset = 24,
) -> Any | HTTPValidationError | None:
    """Clean up orphaned entities

     Delete all entities marked as orphans. Requires 'delete:entities' permission.

    Args:
        namespace (str | Unset): Namespace to clean up (default: 'default') Default: 'default'.
        max_age_hours (int | Unset): Only delete orphans older than this many hours Default: 24.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            namespace=namespace,
            max_age_hours=max_age_hours,
        )
    ).parsed

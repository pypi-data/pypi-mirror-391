from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.o_auth_service_list_response import OAuthServiceListResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    active_only: bool | Unset = True,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["active_only"] = active_only

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/oauth/services",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | HTTPValidationError | OAuthServiceListResponse | None:
    if response.status_code == 200:
        response_200 = OAuthServiceListResponse.from_dict(response.json())

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
) -> Response[Any | HTTPValidationError | OAuthServiceListResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    active_only: bool | Unset = True,
) -> Response[Any | HTTPValidationError | OAuthServiceListResponse]:
    """List Oauth Services

     List all OAuth service configurations

    Args:
        active_only (bool | Unset): Only return active services Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | OAuthServiceListResponse]
    """

    kwargs = _get_kwargs(
        active_only=active_only,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    active_only: bool | Unset = True,
) -> Any | HTTPValidationError | OAuthServiceListResponse | None:
    """List Oauth Services

     List all OAuth service configurations

    Args:
        active_only (bool | Unset): Only return active services Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | OAuthServiceListResponse
    """

    return sync_detailed(
        client=client,
        active_only=active_only,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    active_only: bool | Unset = True,
) -> Response[Any | HTTPValidationError | OAuthServiceListResponse]:
    """List Oauth Services

     List all OAuth service configurations

    Args:
        active_only (bool | Unset): Only return active services Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | OAuthServiceListResponse]
    """

    kwargs = _get_kwargs(
        active_only=active_only,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    active_only: bool | Unset = True,
) -> Any | HTTPValidationError | OAuthServiceListResponse | None:
    """List Oauth Services

     List all OAuth service configurations

    Args:
        active_only (bool | Unset): Only return active services Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | OAuthServiceListResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            active_only=active_only,
        )
    ).parsed

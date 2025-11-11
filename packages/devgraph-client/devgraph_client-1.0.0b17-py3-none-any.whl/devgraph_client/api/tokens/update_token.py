from http import HTTPStatus
from typing import Any, cast
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_token_response import ApiTokenResponse
from ...models.api_token_update import ApiTokenUpdate
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    token_id: UUID,
    *,
    body: ApiTokenUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/api/v1/tokens/{token_id}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | ApiTokenResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = ApiTokenResponse.from_dict(response.json())

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
) -> Response[Any | ApiTokenResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    token_id: UUID,
    *,
    client: AuthenticatedClient,
    body: ApiTokenUpdate,
) -> Response[Any | ApiTokenResponse | HTTPValidationError]:
    """Update Token

     Update an existing API token

    Args:
        token_id (UUID):
        body (ApiTokenUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ApiTokenResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        token_id=token_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    token_id: UUID,
    *,
    client: AuthenticatedClient,
    body: ApiTokenUpdate,
) -> Any | ApiTokenResponse | HTTPValidationError | None:
    """Update Token

     Update an existing API token

    Args:
        token_id (UUID):
        body (ApiTokenUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ApiTokenResponse | HTTPValidationError
    """

    return sync_detailed(
        token_id=token_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    token_id: UUID,
    *,
    client: AuthenticatedClient,
    body: ApiTokenUpdate,
) -> Response[Any | ApiTokenResponse | HTTPValidationError]:
    """Update Token

     Update an existing API token

    Args:
        token_id (UUID):
        body (ApiTokenUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ApiTokenResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        token_id=token_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    token_id: UUID,
    *,
    client: AuthenticatedClient,
    body: ApiTokenUpdate,
) -> Any | ApiTokenResponse | HTTPValidationError | None:
    """Update Token

     Update an existing API token

    Args:
        token_id (UUID):
        body (ApiTokenUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ApiTokenResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            token_id=token_id,
            client=client,
            body=body,
        )
    ).parsed

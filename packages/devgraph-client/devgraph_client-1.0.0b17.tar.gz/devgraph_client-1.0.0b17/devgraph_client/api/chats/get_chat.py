from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.chat_session import ChatSession
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    chat_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/chats/{chat_id}",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | ChatSession | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = ChatSession.from_dict(response.json())

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
) -> Response[Any | ChatSession | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    chat_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Any | ChatSession | HTTPValidationError]:
    """Get Chat

     Retrieve a specific chat session by ID

    Args:
        chat_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ChatSession | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        chat_id=chat_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    chat_id: str,
    *,
    client: AuthenticatedClient,
) -> Any | ChatSession | HTTPValidationError | None:
    """Get Chat

     Retrieve a specific chat session by ID

    Args:
        chat_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ChatSession | HTTPValidationError
    """

    return sync_detailed(
        chat_id=chat_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    chat_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Any | ChatSession | HTTPValidationError]:
    """Get Chat

     Retrieve a specific chat session by ID

    Args:
        chat_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ChatSession | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        chat_id=chat_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    chat_id: str,
    *,
    client: AuthenticatedClient,
) -> Any | ChatSession | HTTPValidationError | None:
    """Get Chat

     Retrieve a specific chat session by ID

    Args:
        chat_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ChatSession | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            chat_id=chat_id,
            client=client,
        )
    ).parsed

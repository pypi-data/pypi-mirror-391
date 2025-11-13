from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.chat_message_router import ChatMessageRouter
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    chat_id: str,
    *,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/chats/{chat_id}/messages",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | HTTPValidationError | list[ChatMessageRouter] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ChatMessageRouter.from_dict(response_200_item_data)

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
) -> Response[Any | HTTPValidationError | list[ChatMessageRouter]]:
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
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> Response[Any | HTTPValidationError | list[ChatMessageRouter]]:
    """Get Chat Messages

     Retrieve all messages from a specific chat session

    Args:
        chat_id (str):
        limit (int | Unset):  Default: 100.
        offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | list[ChatMessageRouter]]
    """

    kwargs = _get_kwargs(
        chat_id=chat_id,
        limit=limit,
        offset=offset,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    chat_id: str,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> Any | HTTPValidationError | list[ChatMessageRouter] | None:
    """Get Chat Messages

     Retrieve all messages from a specific chat session

    Args:
        chat_id (str):
        limit (int | Unset):  Default: 100.
        offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | list[ChatMessageRouter]
    """

    return sync_detailed(
        chat_id=chat_id,
        client=client,
        limit=limit,
        offset=offset,
    ).parsed


async def asyncio_detailed(
    chat_id: str,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> Response[Any | HTTPValidationError | list[ChatMessageRouter]]:
    """Get Chat Messages

     Retrieve all messages from a specific chat session

    Args:
        chat_id (str):
        limit (int | Unset):  Default: 100.
        offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | list[ChatMessageRouter]]
    """

    kwargs = _get_kwargs(
        chat_id=chat_id,
        limit=limit,
        offset=offset,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    chat_id: str,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> Any | HTTPValidationError | list[ChatMessageRouter] | None:
    """Get Chat Messages

     Retrieve all messages from a specific chat session

    Args:
        chat_id (str):
        limit (int | Unset):  Default: 100.
        offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | list[ChatMessageRouter]
    """

    return (
        await asyncio_detailed(
            chat_id=chat_id,
            client=client,
            limit=limit,
            offset=offset,
        )
    ).parsed

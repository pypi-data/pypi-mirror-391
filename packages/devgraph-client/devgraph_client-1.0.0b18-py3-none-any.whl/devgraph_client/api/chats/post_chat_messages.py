from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.chat_message_create import ChatMessageCreate
from ...models.chat_message_router import ChatMessageRouter
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    chat_id: str,
    *,
    body: list[ChatMessageCreate],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v1/chats/{chat_id}/messages",
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
) -> Any | HTTPValidationError | list[ChatMessageRouter] | None:
    if response.status_code == 201:
        response_201 = []
        _response_201 = response.json()
        for response_201_item_data in _response_201:
            response_201_item = ChatMessageRouter.from_dict(response_201_item_data)

            response_201.append(response_201_item)

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
    body: list[ChatMessageCreate],
) -> Response[Any | HTTPValidationError | list[ChatMessageRouter]]:
    """Post Chat Messages

     Add one or more messages to a chat session

    Args:
        chat_id (str):
        body (list[ChatMessageCreate]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | list[ChatMessageRouter]]
    """

    kwargs = _get_kwargs(
        chat_id=chat_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    chat_id: str,
    *,
    client: AuthenticatedClient,
    body: list[ChatMessageCreate],
) -> Any | HTTPValidationError | list[ChatMessageRouter] | None:
    """Post Chat Messages

     Add one or more messages to a chat session

    Args:
        chat_id (str):
        body (list[ChatMessageCreate]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | list[ChatMessageRouter]
    """

    return sync_detailed(
        chat_id=chat_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    chat_id: str,
    *,
    client: AuthenticatedClient,
    body: list[ChatMessageCreate],
) -> Response[Any | HTTPValidationError | list[ChatMessageRouter]]:
    """Post Chat Messages

     Add one or more messages to a chat session

    Args:
        chat_id (str):
        body (list[ChatMessageCreate]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | list[ChatMessageRouter]]
    """

    kwargs = _get_kwargs(
        chat_id=chat_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    chat_id: str,
    *,
    client: AuthenticatedClient,
    body: list[ChatMessageCreate],
) -> Any | HTTPValidationError | list[ChatMessageRouter] | None:
    """Post Chat Messages

     Add one or more messages to a chat session

    Args:
        chat_id (str):
        body (list[ChatMessageCreate]):

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
            body=body,
        )
    ).parsed

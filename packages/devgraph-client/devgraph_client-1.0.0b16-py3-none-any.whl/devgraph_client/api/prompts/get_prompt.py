from http import HTTPStatus
from typing import Any, cast
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.prompt_response import PromptResponse
from ...types import Response


def _get_kwargs(
    prompt_id: UUID,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/prompts/{prompt_id}",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | HTTPValidationError | PromptResponse | None:
    if response.status_code == 200:
        response_200 = PromptResponse.from_dict(response.json())

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
) -> Response[Any | HTTPValidationError | PromptResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    prompt_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[Any | HTTPValidationError | PromptResponse]:
    """Get Prompt

     Retrieve a specific prompt template by ID

    Args:
        prompt_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | PromptResponse]
    """

    kwargs = _get_kwargs(
        prompt_id=prompt_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    prompt_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Any | HTTPValidationError | PromptResponse | None:
    """Get Prompt

     Retrieve a specific prompt template by ID

    Args:
        prompt_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | PromptResponse
    """

    return sync_detailed(
        prompt_id=prompt_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    prompt_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[Any | HTTPValidationError | PromptResponse]:
    """Get Prompt

     Retrieve a specific prompt template by ID

    Args:
        prompt_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | PromptResponse]
    """

    kwargs = _get_kwargs(
        prompt_id=prompt_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    prompt_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Any | HTTPValidationError | PromptResponse | None:
    """Get Prompt

     Retrieve a specific prompt template by ID

    Args:
        prompt_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | PromptResponse
    """

    return (
        await asyncio_detailed(
            prompt_id=prompt_id,
            client=client,
        )
    ).parsed

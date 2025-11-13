from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.null_boolean_enum import NullBooleanEnum
from ...models.prompt_response import PromptResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    active: NullBooleanEnum | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_active: str | Unset = UNSET
    if not isinstance(active, Unset):
        json_active = active.value

    params["active"] = json_active

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/prompts",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | HTTPValidationError | list[PromptResponse] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = PromptResponse.from_dict(response_200_item_data)

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
) -> Response[Any | HTTPValidationError | list[PromptResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    active: NullBooleanEnum | Unset = UNSET,
) -> Response[Any | HTTPValidationError | list[PromptResponse]]:
    """List Prompts

     List all prompt templates for the environment, optionally filtered by active status

    Args:
        active (NullBooleanEnum | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | list[PromptResponse]]
    """

    kwargs = _get_kwargs(
        active=active,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    active: NullBooleanEnum | Unset = UNSET,
) -> Any | HTTPValidationError | list[PromptResponse] | None:
    """List Prompts

     List all prompt templates for the environment, optionally filtered by active status

    Args:
        active (NullBooleanEnum | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | list[PromptResponse]
    """

    return sync_detailed(
        client=client,
        active=active,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    active: NullBooleanEnum | Unset = UNSET,
) -> Response[Any | HTTPValidationError | list[PromptResponse]]:
    """List Prompts

     List all prompt templates for the environment, optionally filtered by active status

    Args:
        active (NullBooleanEnum | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | list[PromptResponse]]
    """

    kwargs = _get_kwargs(
        active=active,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    active: NullBooleanEnum | Unset = UNSET,
) -> Any | HTTPValidationError | list[PromptResponse] | None:
    """List Prompts

     List all prompt templates for the environment, optionally filtered by active status

    Args:
        active (NullBooleanEnum | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | list[PromptResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            active=active,
        )
    ).parsed

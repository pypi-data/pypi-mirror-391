from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.anthropic_model_provider_response import AnthropicModelProviderResponse
from ...models.open_ai_model_provider_response import OpenAIModelProviderResponse
from ...models.xai_model_provider_response import XAIModelProviderResponse
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/models/providers",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | list[AnthropicModelProviderResponse | OpenAIModelProviderResponse | XAIModelProviderResponse] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:

            def _parse_response_200_item(
                data: object,
            ) -> AnthropicModelProviderResponse | OpenAIModelProviderResponse | XAIModelProviderResponse:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_model_provider_response_type_0 = OpenAIModelProviderResponse.from_dict(data)

                    return componentsschemas_model_provider_response_type_0
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_model_provider_response_type_1 = XAIModelProviderResponse.from_dict(data)

                    return componentsschemas_model_provider_response_type_1
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_model_provider_response_type_2 = AnthropicModelProviderResponse.from_dict(data)

                return componentsschemas_model_provider_response_type_2

            response_200_item = _parse_response_200_item(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | list[AnthropicModelProviderResponse | OpenAIModelProviderResponse | XAIModelProviderResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[Any | list[AnthropicModelProviderResponse | OpenAIModelProviderResponse | XAIModelProviderResponse]]:
    """Get Modelproviders

     List all model provider configurations for the authenticated user and environment

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | list[AnthropicModelProviderResponse | OpenAIModelProviderResponse | XAIModelProviderResponse]]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
) -> Any | list[AnthropicModelProviderResponse | OpenAIModelProviderResponse | XAIModelProviderResponse] | None:
    """Get Modelproviders

     List all model provider configurations for the authenticated user and environment

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | list[AnthropicModelProviderResponse | OpenAIModelProviderResponse | XAIModelProviderResponse]
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[Any | list[AnthropicModelProviderResponse | OpenAIModelProviderResponse | XAIModelProviderResponse]]:
    """Get Modelproviders

     List all model provider configurations for the authenticated user and environment

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | list[AnthropicModelProviderResponse | OpenAIModelProviderResponse | XAIModelProviderResponse]]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
) -> Any | list[AnthropicModelProviderResponse | OpenAIModelProviderResponse | XAIModelProviderResponse] | None:
    """Get Modelproviders

     List all model provider configurations for the authenticated user and environment

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | list[AnthropicModelProviderResponse | OpenAIModelProviderResponse | XAIModelProviderResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed

from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.anthropic_model_provider_response import AnthropicModelProviderResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.model_provider_create import ModelProviderCreate
from ...models.open_ai_model_provider_response import OpenAIModelProviderResponse
from ...models.xai_model_provider_response import XAIModelProviderResponse
from ...types import Response


def _get_kwargs(
    *,
    body: ModelProviderCreate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/models/providers",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    AnthropicModelProviderResponse
    | OpenAIModelProviderResponse
    | XAIModelProviderResponse
    | Any
    | HTTPValidationError
    | None
):
    if response.status_code == 201:

        def _parse_response_201(
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

        response_201 = _parse_response_201(response.json())

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
) -> Response[
    AnthropicModelProviderResponse | OpenAIModelProviderResponse | XAIModelProviderResponse | Any | HTTPValidationError
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: ModelProviderCreate,
) -> Response[
    AnthropicModelProviderResponse | OpenAIModelProviderResponse | XAIModelProviderResponse | Any | HTTPValidationError
]:
    """Create Modelprovider

     Create a new model provider configuration

    Args:
        body (ModelProviderCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AnthropicModelProviderResponse | OpenAIModelProviderResponse | XAIModelProviderResponse | Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: ModelProviderCreate,
) -> (
    AnthropicModelProviderResponse
    | OpenAIModelProviderResponse
    | XAIModelProviderResponse
    | Any
    | HTTPValidationError
    | None
):
    """Create Modelprovider

     Create a new model provider configuration

    Args:
        body (ModelProviderCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AnthropicModelProviderResponse | OpenAIModelProviderResponse | XAIModelProviderResponse | Any | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: ModelProviderCreate,
) -> Response[
    AnthropicModelProviderResponse | OpenAIModelProviderResponse | XAIModelProviderResponse | Any | HTTPValidationError
]:
    """Create Modelprovider

     Create a new model provider configuration

    Args:
        body (ModelProviderCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AnthropicModelProviderResponse | OpenAIModelProviderResponse | XAIModelProviderResponse | Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: ModelProviderCreate,
) -> (
    AnthropicModelProviderResponse
    | OpenAIModelProviderResponse
    | XAIModelProviderResponse
    | Any
    | HTTPValidationError
    | None
):
    """Create Modelprovider

     Create a new model provider configuration

    Args:
        body (ModelProviderCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AnthropicModelProviderResponse | OpenAIModelProviderResponse | XAIModelProviderResponse | Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed

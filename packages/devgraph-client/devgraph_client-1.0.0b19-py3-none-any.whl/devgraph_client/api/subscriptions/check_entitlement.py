from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.entitlement_check_response import EntitlementCheckResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    entitlement_type: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/entitlements/check/{entitlement_type}",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | EntitlementCheckResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = EntitlementCheckResponse.from_dict(response.json())

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
) -> Response[Any | EntitlementCheckResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    entitlement_type: str,
    *,
    client: AuthenticatedClient,
) -> Response[Any | EntitlementCheckResponse | HTTPValidationError]:
    """Check Entitlement

     Check a specific entitlement for the authenticated user

    Args:
        entitlement_type (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | EntitlementCheckResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        entitlement_type=entitlement_type,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    entitlement_type: str,
    *,
    client: AuthenticatedClient,
) -> Any | EntitlementCheckResponse | HTTPValidationError | None:
    """Check Entitlement

     Check a specific entitlement for the authenticated user

    Args:
        entitlement_type (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | EntitlementCheckResponse | HTTPValidationError
    """

    return sync_detailed(
        entitlement_type=entitlement_type,
        client=client,
    ).parsed


async def asyncio_detailed(
    entitlement_type: str,
    *,
    client: AuthenticatedClient,
) -> Response[Any | EntitlementCheckResponse | HTTPValidationError]:
    """Check Entitlement

     Check a specific entitlement for the authenticated user

    Args:
        entitlement_type (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | EntitlementCheckResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        entitlement_type=entitlement_type,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    entitlement_type: str,
    *,
    client: AuthenticatedClient,
) -> Any | EntitlementCheckResponse | HTTPValidationError | None:
    """Check Entitlement

     Check a specific entitlement for the authenticated user

    Args:
        entitlement_type (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | EntitlementCheckResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            entitlement_type=entitlement_type,
            client=client,
        )
    ).parsed

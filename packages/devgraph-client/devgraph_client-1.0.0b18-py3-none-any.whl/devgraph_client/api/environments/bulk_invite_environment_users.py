from http import HTTPStatus
from typing import Any, cast
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.environment_user_bulk_invite import EnvironmentUserBulkInvite
from ...models.environment_user_response import EnvironmentUserResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    environment_id: UUID,
    *,
    body: EnvironmentUserBulkInvite,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v1/environments/{environment_id}/users/bulk-invite",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | HTTPValidationError | list[EnvironmentUserResponse] | None:
    if response.status_code == 201:
        response_201 = []
        _response_201 = response.json()
        for response_201_item_data in _response_201:
            response_201_item = EnvironmentUserResponse.from_dict(response_201_item_data)

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
) -> Response[Any | HTTPValidationError | list[EnvironmentUserResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    environment_id: UUID,
    *,
    client: AuthenticatedClient,
    body: EnvironmentUserBulkInvite,
) -> Response[Any | HTTPValidationError | list[EnvironmentUserResponse]]:
    """Bulk Invite Environment Users

     Bulk invite multiple users to an environment

    Args:
        environment_id (UUID):
        body (EnvironmentUserBulkInvite):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | list[EnvironmentUserResponse]]
    """

    kwargs = _get_kwargs(
        environment_id=environment_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    environment_id: UUID,
    *,
    client: AuthenticatedClient,
    body: EnvironmentUserBulkInvite,
) -> Any | HTTPValidationError | list[EnvironmentUserResponse] | None:
    """Bulk Invite Environment Users

     Bulk invite multiple users to an environment

    Args:
        environment_id (UUID):
        body (EnvironmentUserBulkInvite):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | list[EnvironmentUserResponse]
    """

    return sync_detailed(
        environment_id=environment_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    environment_id: UUID,
    *,
    client: AuthenticatedClient,
    body: EnvironmentUserBulkInvite,
) -> Response[Any | HTTPValidationError | list[EnvironmentUserResponse]]:
    """Bulk Invite Environment Users

     Bulk invite multiple users to an environment

    Args:
        environment_id (UUID):
        body (EnvironmentUserBulkInvite):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | list[EnvironmentUserResponse]]
    """

    kwargs = _get_kwargs(
        environment_id=environment_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    environment_id: UUID,
    *,
    client: AuthenticatedClient,
    body: EnvironmentUserBulkInvite,
) -> Any | HTTPValidationError | list[EnvironmentUserResponse] | None:
    """Bulk Invite Environment Users

     Bulk invite multiple users to an environment

    Args:
        environment_id (UUID):
        body (EnvironmentUserBulkInvite):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | list[EnvironmentUserResponse]
    """

    return (
        await asyncio_detailed(
            environment_id=environment_id,
            client=client,
            body=body,
        )
    ).parsed

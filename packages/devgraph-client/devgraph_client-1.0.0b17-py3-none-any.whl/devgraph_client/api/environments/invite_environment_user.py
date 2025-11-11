from http import HTTPStatus
from typing import Any, cast
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.environment_user_invite import EnvironmentUserInvite
from ...models.environment_user_response import EnvironmentUserResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    environment_id: UUID,
    *,
    body: EnvironmentUserInvite,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v1/environments/{environment_id}/users/invite",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | EnvironmentUserResponse | HTTPValidationError | None:
    if response.status_code == 201:
        response_201 = EnvironmentUserResponse.from_dict(response.json())

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
) -> Response[Any | EnvironmentUserResponse | HTTPValidationError]:
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
    body: EnvironmentUserInvite,
) -> Response[Any | EnvironmentUserResponse | HTTPValidationError]:
    """Invite Environment User

     Invite a user to an environment

    Args:
        environment_id (UUID):
        body (EnvironmentUserInvite):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | EnvironmentUserResponse | HTTPValidationError]
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
    body: EnvironmentUserInvite,
) -> Any | EnvironmentUserResponse | HTTPValidationError | None:
    """Invite Environment User

     Invite a user to an environment

    Args:
        environment_id (UUID):
        body (EnvironmentUserInvite):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | EnvironmentUserResponse | HTTPValidationError
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
    body: EnvironmentUserInvite,
) -> Response[Any | EnvironmentUserResponse | HTTPValidationError]:
    """Invite Environment User

     Invite a user to an environment

    Args:
        environment_id (UUID):
        body (EnvironmentUserInvite):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | EnvironmentUserResponse | HTTPValidationError]
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
    body: EnvironmentUserInvite,
) -> Any | EnvironmentUserResponse | HTTPValidationError | None:
    """Invite Environment User

     Invite a user to an environment

    Args:
        environment_id (UUID):
        body (EnvironmentUserInvite):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | EnvironmentUserResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            environment_id=environment_id,
            client=client,
            body=body,
        )
    ).parsed

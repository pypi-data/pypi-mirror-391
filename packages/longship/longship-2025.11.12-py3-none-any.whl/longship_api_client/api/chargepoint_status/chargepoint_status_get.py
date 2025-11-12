from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.chargepoint_status_dto import ChargepointStatusDto
from ...models.longship_error import LongshipError
from ...types import Response


def _get_kwargs(
    id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/chargepoint/{id}/status",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ChargepointStatusDto | LongshipError | None:
    if response.status_code == 200:
        response_200 = ChargepointStatusDto.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = LongshipError.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = LongshipError.from_dict(response.json())

        return response_403

    if response.status_code == 404:
        response_404 = LongshipError.from_dict(response.json())

        return response_404

    if response.status_code == 500:
        response_500 = LongshipError.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ChargepointStatusDto | LongshipError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ChargepointStatusDto | LongshipError]:
    """Gets the chargepointstatus.

     Gets the chargepointstatus base on the id.

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ChargepointStatusDto | LongshipError]
    """

    kwargs = _get_kwargs(
        id=id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: str,
    *,
    client: AuthenticatedClient | Client,
) -> ChargepointStatusDto | LongshipError | None:
    """Gets the chargepointstatus.

     Gets the chargepointstatus base on the id.

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ChargepointStatusDto | LongshipError
    """

    return sync_detailed(
        id=id,
        client=client,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ChargepointStatusDto | LongshipError]:
    """Gets the chargepointstatus.

     Gets the chargepointstatus base on the id.

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ChargepointStatusDto | LongshipError]
    """

    kwargs = _get_kwargs(
        id=id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient | Client,
) -> ChargepointStatusDto | LongshipError | None:
    """Gets the chargepointstatus.

     Gets the chargepointstatus base on the id.

    Args:
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ChargepointStatusDto | LongshipError
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
        )
    ).parsed

from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.longship_error import LongshipError
from ...types import Response


def _get_kwargs(
    id: str,
    charge_point_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/v1/locations/{id}/chargepoints/{charge_point_id}",
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | LongshipError | None:
    if response.status_code == 202:
        response_202 = cast(Any, None)
        return response_202

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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | LongshipError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: str,
    charge_point_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | LongshipError]:
    """Deletes a relation between location and charge point.

     Deletes a relation between location and charge point.

    Args:
        id (str):
        charge_point_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | LongshipError]
    """

    kwargs = _get_kwargs(
        id=id,
        charge_point_id=charge_point_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: str,
    charge_point_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Any | LongshipError | None:
    """Deletes a relation between location and charge point.

     Deletes a relation between location and charge point.

    Args:
        id (str):
        charge_point_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | LongshipError
    """

    return sync_detailed(
        id=id,
        charge_point_id=charge_point_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    id: str,
    charge_point_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | LongshipError]:
    """Deletes a relation between location and charge point.

     Deletes a relation between location and charge point.

    Args:
        id (str):
        charge_point_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | LongshipError]
    """

    kwargs = _get_kwargs(
        id=id,
        charge_point_id=charge_point_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    charge_point_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Any | LongshipError | None:
    """Deletes a relation between location and charge point.

     Deletes a relation between location and charge point.

    Args:
        id (str):
        charge_point_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | LongshipError
    """

    return (
        await asyncio_detailed(
            id=id,
            charge_point_id=charge_point_id,
            client=client,
        )
    ).parsed

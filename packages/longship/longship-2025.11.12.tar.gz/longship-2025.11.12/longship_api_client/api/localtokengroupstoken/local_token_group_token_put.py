from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.local_token_group_token_put_dto import LocalTokenGroupTokenPutDto
from ...models.longship_error import LongshipError
from ...types import Response


def _get_kwargs(
    id: str,
    token_uid: str,
    *,
    body: LocalTokenGroupTokenPutDto,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/v1/localtokengroups/{id}/token/{token_uid}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | LongshipError | None:
    if response.status_code == 202:
        response_202 = cast(Any, None)
        return response_202

    if response.status_code == 400:
        response_400 = LongshipError.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = LongshipError.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = LongshipError.from_dict(response.json())

        return response_403

    if response.status_code == 404:
        response_404 = LongshipError.from_dict(response.json())

        return response_404

    if response.status_code == 409:
        response_409 = LongshipError.from_dict(response.json())

        return response_409

    if response.status_code == 422:
        response_422 = LongshipError.from_dict(response.json())

        return response_422

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
    token_uid: str,
    *,
    client: AuthenticatedClient | Client,
    body: LocalTokenGroupTokenPutDto,
) -> Response[Any | LongshipError]:
    """Updates a localtokengrouptoken.

     Updates a localtokengrouptoken.

    Args:
        id (str):
        token_uid (str):
        body (LocalTokenGroupTokenPutDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | LongshipError]
    """

    kwargs = _get_kwargs(
        id=id,
        token_uid=token_uid,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: str,
    token_uid: str,
    *,
    client: AuthenticatedClient | Client,
    body: LocalTokenGroupTokenPutDto,
) -> Any | LongshipError | None:
    """Updates a localtokengrouptoken.

     Updates a localtokengrouptoken.

    Args:
        id (str):
        token_uid (str):
        body (LocalTokenGroupTokenPutDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | LongshipError
    """

    return sync_detailed(
        id=id,
        token_uid=token_uid,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    id: str,
    token_uid: str,
    *,
    client: AuthenticatedClient | Client,
    body: LocalTokenGroupTokenPutDto,
) -> Response[Any | LongshipError]:
    """Updates a localtokengrouptoken.

     Updates a localtokengrouptoken.

    Args:
        id (str):
        token_uid (str):
        body (LocalTokenGroupTokenPutDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | LongshipError]
    """

    kwargs = _get_kwargs(
        id=id,
        token_uid=token_uid,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    token_uid: str,
    *,
    client: AuthenticatedClient | Client,
    body: LocalTokenGroupTokenPutDto,
) -> Any | LongshipError | None:
    """Updates a localtokengrouptoken.

     Updates a localtokengrouptoken.

    Args:
        id (str):
        token_uid (str):
        body (LocalTokenGroupTokenPutDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | LongshipError
    """

    return (
        await asyncio_detailed(
            id=id,
            token_uid=token_uid,
            client=client,
            body=body,
        )
    ).parsed

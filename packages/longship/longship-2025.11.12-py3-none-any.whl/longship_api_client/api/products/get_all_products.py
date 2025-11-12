from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_all_products_order_by import GetAllProductsOrderBy
from ...models.longship_error import LongshipError
from ...models.product_dto import ProductDto
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    skip: int | Unset = UNSET,
    take: int | Unset = UNSET,
    search: str | Unset = UNSET,
    order_by: GetAllProductsOrderBy | Unset = GetAllProductsOrderBy.VALUE_0,
    descending: bool | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["skip"] = skip

    params["take"] = take

    params["search"] = search

    json_order_by: int | Unset = UNSET
    if not isinstance(order_by, Unset):
        json_order_by = order_by.value

    params["orderBy"] = json_order_by

    params["descending"] = descending

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/products",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> LongshipError | list[ProductDto] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemasproduct_dto_array_item_data in _response_200:
            componentsschemasproduct_dto_array_item = ProductDto.from_dict(componentsschemasproduct_dto_array_item_data)

            response_200.append(componentsschemasproduct_dto_array_item)

        return response_200

    if response.status_code == 401:
        response_401 = LongshipError.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = LongshipError.from_dict(response.json())

        return response_403

    if response.status_code == 500:
        response_500 = LongshipError.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[LongshipError | list[ProductDto]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = UNSET,
    take: int | Unset = UNSET,
    search: str | Unset = UNSET,
    order_by: GetAllProductsOrderBy | Unset = GetAllProductsOrderBy.VALUE_0,
    descending: bool | Unset = UNSET,
) -> Response[LongshipError | list[ProductDto]]:
    """Get a list of products.

     Get a paged list of products, taken the filters into account.

    Args:
        skip (int | Unset):
        take (int | Unset):
        search (str | Unset):
        order_by (GetAllProductsOrderBy | Unset):  Default: GetAllProductsOrderBy.VALUE_0.
        descending (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[LongshipError | list[ProductDto]]
    """

    kwargs = _get_kwargs(
        skip=skip,
        take=take,
        search=search,
        order_by=order_by,
        descending=descending,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = UNSET,
    take: int | Unset = UNSET,
    search: str | Unset = UNSET,
    order_by: GetAllProductsOrderBy | Unset = GetAllProductsOrderBy.VALUE_0,
    descending: bool | Unset = UNSET,
) -> LongshipError | list[ProductDto] | None:
    """Get a list of products.

     Get a paged list of products, taken the filters into account.

    Args:
        skip (int | Unset):
        take (int | Unset):
        search (str | Unset):
        order_by (GetAllProductsOrderBy | Unset):  Default: GetAllProductsOrderBy.VALUE_0.
        descending (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        LongshipError | list[ProductDto]
    """

    return sync_detailed(
        client=client,
        skip=skip,
        take=take,
        search=search,
        order_by=order_by,
        descending=descending,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = UNSET,
    take: int | Unset = UNSET,
    search: str | Unset = UNSET,
    order_by: GetAllProductsOrderBy | Unset = GetAllProductsOrderBy.VALUE_0,
    descending: bool | Unset = UNSET,
) -> Response[LongshipError | list[ProductDto]]:
    """Get a list of products.

     Get a paged list of products, taken the filters into account.

    Args:
        skip (int | Unset):
        take (int | Unset):
        search (str | Unset):
        order_by (GetAllProductsOrderBy | Unset):  Default: GetAllProductsOrderBy.VALUE_0.
        descending (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[LongshipError | list[ProductDto]]
    """

    kwargs = _get_kwargs(
        skip=skip,
        take=take,
        search=search,
        order_by=order_by,
        descending=descending,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = UNSET,
    take: int | Unset = UNSET,
    search: str | Unset = UNSET,
    order_by: GetAllProductsOrderBy | Unset = GetAllProductsOrderBy.VALUE_0,
    descending: bool | Unset = UNSET,
) -> LongshipError | list[ProductDto] | None:
    """Get a list of products.

     Get a paged list of products, taken the filters into account.

    Args:
        skip (int | Unset):
        take (int | Unset):
        search (str | Unset):
        order_by (GetAllProductsOrderBy | Unset):  Default: GetAllProductsOrderBy.VALUE_0.
        descending (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        LongshipError | list[ProductDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            skip=skip,
            take=take,
            search=search,
            order_by=order_by,
            descending=descending,
        )
    ).parsed

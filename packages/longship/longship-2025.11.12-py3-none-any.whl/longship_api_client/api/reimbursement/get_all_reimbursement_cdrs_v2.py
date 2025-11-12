import datetime
from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_all_reimbursement_cdrs_v2_order_by import GetAllReimbursementCdrsV2OrderBy
from ...models.longship_error import LongshipError
from ...models.reimbursement_cdr_dto import ReimbursementCdrDto
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    skip: int | Unset = UNSET,
    take: int | Unset = UNSET,
    search: str | Unset = UNSET,
    providerexclude: str | Unset = UNSET,
    order_by: GetAllReimbursementCdrsV2OrderBy | Unset = GetAllReimbursementCdrsV2OrderBy.STARTDATETIME,
    descending: bool | Unset = UNSET,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["skip"] = skip

    params["take"] = take

    params["search"] = search

    params["providerexclude"] = providerexclude

    json_order_by: str | Unset = UNSET
    if not isinstance(order_by, Unset):
        json_order_by = order_by.value

    params["orderBy"] = json_order_by

    params["descending"] = descending

    json_from_: str | Unset = UNSET
    if not isinstance(from_, Unset):
        json_from_ = from_.isoformat()
    params["from"] = json_from_

    json_to: str | Unset = UNSET
    if not isinstance(to, Unset):
        json_to = to.isoformat()
    params["to"] = json_to

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/reimbursementcdrs",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> LongshipError | list[ReimbursementCdrDto] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemasreimbursement_cdr_dto_array_item_data in _response_200:
            componentsschemasreimbursement_cdr_dto_array_item = ReimbursementCdrDto.from_dict(
                componentsschemasreimbursement_cdr_dto_array_item_data
            )

            response_200.append(componentsschemasreimbursement_cdr_dto_array_item)

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
) -> Response[LongshipError | list[ReimbursementCdrDto]]:
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
    providerexclude: str | Unset = UNSET,
    order_by: GetAllReimbursementCdrsV2OrderBy | Unset = GetAllReimbursementCdrsV2OrderBy.STARTDATETIME,
    descending: bool | Unset = UNSET,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
) -> Response[LongshipError | list[ReimbursementCdrDto]]:
    """Get a list of reimbursementcdrs.

     Get a paged list of reimbursementcdrs, taken the filters into account.

    Args:
        skip (int | Unset):
        take (int | Unset):
        search (str | Unset):
        providerexclude (str | Unset):
        order_by (GetAllReimbursementCdrsV2OrderBy | Unset):  Default:
            GetAllReimbursementCdrsV2OrderBy.STARTDATETIME.
        descending (bool | Unset):
        from_ (datetime.datetime | Unset):
        to (datetime.datetime | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[LongshipError | list[ReimbursementCdrDto]]
    """

    kwargs = _get_kwargs(
        skip=skip,
        take=take,
        search=search,
        providerexclude=providerexclude,
        order_by=order_by,
        descending=descending,
        from_=from_,
        to=to,
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
    providerexclude: str | Unset = UNSET,
    order_by: GetAllReimbursementCdrsV2OrderBy | Unset = GetAllReimbursementCdrsV2OrderBy.STARTDATETIME,
    descending: bool | Unset = UNSET,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
) -> LongshipError | list[ReimbursementCdrDto] | None:
    """Get a list of reimbursementcdrs.

     Get a paged list of reimbursementcdrs, taken the filters into account.

    Args:
        skip (int | Unset):
        take (int | Unset):
        search (str | Unset):
        providerexclude (str | Unset):
        order_by (GetAllReimbursementCdrsV2OrderBy | Unset):  Default:
            GetAllReimbursementCdrsV2OrderBy.STARTDATETIME.
        descending (bool | Unset):
        from_ (datetime.datetime | Unset):
        to (datetime.datetime | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        LongshipError | list[ReimbursementCdrDto]
    """

    return sync_detailed(
        client=client,
        skip=skip,
        take=take,
        search=search,
        providerexclude=providerexclude,
        order_by=order_by,
        descending=descending,
        from_=from_,
        to=to,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = UNSET,
    take: int | Unset = UNSET,
    search: str | Unset = UNSET,
    providerexclude: str | Unset = UNSET,
    order_by: GetAllReimbursementCdrsV2OrderBy | Unset = GetAllReimbursementCdrsV2OrderBy.STARTDATETIME,
    descending: bool | Unset = UNSET,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
) -> Response[LongshipError | list[ReimbursementCdrDto]]:
    """Get a list of reimbursementcdrs.

     Get a paged list of reimbursementcdrs, taken the filters into account.

    Args:
        skip (int | Unset):
        take (int | Unset):
        search (str | Unset):
        providerexclude (str | Unset):
        order_by (GetAllReimbursementCdrsV2OrderBy | Unset):  Default:
            GetAllReimbursementCdrsV2OrderBy.STARTDATETIME.
        descending (bool | Unset):
        from_ (datetime.datetime | Unset):
        to (datetime.datetime | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[LongshipError | list[ReimbursementCdrDto]]
    """

    kwargs = _get_kwargs(
        skip=skip,
        take=take,
        search=search,
        providerexclude=providerexclude,
        order_by=order_by,
        descending=descending,
        from_=from_,
        to=to,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = UNSET,
    take: int | Unset = UNSET,
    search: str | Unset = UNSET,
    providerexclude: str | Unset = UNSET,
    order_by: GetAllReimbursementCdrsV2OrderBy | Unset = GetAllReimbursementCdrsV2OrderBy.STARTDATETIME,
    descending: bool | Unset = UNSET,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
) -> LongshipError | list[ReimbursementCdrDto] | None:
    """Get a list of reimbursementcdrs.

     Get a paged list of reimbursementcdrs, taken the filters into account.

    Args:
        skip (int | Unset):
        take (int | Unset):
        search (str | Unset):
        providerexclude (str | Unset):
        order_by (GetAllReimbursementCdrsV2OrderBy | Unset):  Default:
            GetAllReimbursementCdrsV2OrderBy.STARTDATETIME.
        descending (bool | Unset):
        from_ (datetime.datetime | Unset):
        to (datetime.datetime | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        LongshipError | list[ReimbursementCdrDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            skip=skip,
            take=take,
            search=search,
            providerexclude=providerexclude,
            order_by=order_by,
            descending=descending,
            from_=from_,
            to=to,
        )
    ).parsed

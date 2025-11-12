import datetime
from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.charge_point_authorize_get_dto import ChargePointAuthorizeGetDto
from ...models.longship_error import LongshipError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: str,
    *,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
    descending: bool | Unset = UNSET,
    status: str | Unset = UNSET,
    search: str | Unset = UNSET,
    skip: int | Unset = UNSET,
    take: int | Unset = UNSET,
    idtag: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_from_: str | Unset = UNSET
    if not isinstance(from_, Unset):
        json_from_ = from_.isoformat()
    params["from"] = json_from_

    json_to: str | Unset = UNSET
    if not isinstance(to, Unset):
        json_to = to.isoformat()
    params["to"] = json_to

    params["descending"] = descending

    params["status"] = status

    params["search"] = search

    params["skip"] = skip

    params["take"] = take

    params["idtag"] = idtag

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/chargepoints/{id}/authorization",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> LongshipError | list[ChargePointAuthorizeGetDto] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemascharge_point_authorize_get_dto_array_item_data in _response_200:
            componentsschemascharge_point_authorize_get_dto_array_item = ChargePointAuthorizeGetDto.from_dict(
                componentsschemascharge_point_authorize_get_dto_array_item_data
            )

            response_200.append(componentsschemascharge_point_authorize_get_dto_array_item)

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
) -> Response[LongshipError | list[ChargePointAuthorizeGetDto]]:
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
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
    descending: bool | Unset = UNSET,
    status: str | Unset = UNSET,
    search: str | Unset = UNSET,
    skip: int | Unset = UNSET,
    take: int | Unset = UNSET,
    idtag: str | Unset = UNSET,
) -> Response[LongshipError | list[ChargePointAuthorizeGetDto]]:
    """Get a list of chargepointauthorizations.

     Get a paged list of chargepointauthorizations, taken the filters into account.

    Args:
        id (str):
        from_ (datetime.datetime | Unset):
        to (datetime.datetime | Unset):
        descending (bool | Unset):
        status (str | Unset):
        search (str | Unset):
        skip (int | Unset):
        take (int | Unset):
        idtag (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[LongshipError | list[ChargePointAuthorizeGetDto]]
    """

    kwargs = _get_kwargs(
        id=id,
        from_=from_,
        to=to,
        descending=descending,
        status=status,
        search=search,
        skip=skip,
        take=take,
        idtag=idtag,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
    descending: bool | Unset = UNSET,
    status: str | Unset = UNSET,
    search: str | Unset = UNSET,
    skip: int | Unset = UNSET,
    take: int | Unset = UNSET,
    idtag: str | Unset = UNSET,
) -> LongshipError | list[ChargePointAuthorizeGetDto] | None:
    """Get a list of chargepointauthorizations.

     Get a paged list of chargepointauthorizations, taken the filters into account.

    Args:
        id (str):
        from_ (datetime.datetime | Unset):
        to (datetime.datetime | Unset):
        descending (bool | Unset):
        status (str | Unset):
        search (str | Unset):
        skip (int | Unset):
        take (int | Unset):
        idtag (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        LongshipError | list[ChargePointAuthorizeGetDto]
    """

    return sync_detailed(
        id=id,
        client=client,
        from_=from_,
        to=to,
        descending=descending,
        status=status,
        search=search,
        skip=skip,
        take=take,
        idtag=idtag,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
    descending: bool | Unset = UNSET,
    status: str | Unset = UNSET,
    search: str | Unset = UNSET,
    skip: int | Unset = UNSET,
    take: int | Unset = UNSET,
    idtag: str | Unset = UNSET,
) -> Response[LongshipError | list[ChargePointAuthorizeGetDto]]:
    """Get a list of chargepointauthorizations.

     Get a paged list of chargepointauthorizations, taken the filters into account.

    Args:
        id (str):
        from_ (datetime.datetime | Unset):
        to (datetime.datetime | Unset):
        descending (bool | Unset):
        status (str | Unset):
        search (str | Unset):
        skip (int | Unset):
        take (int | Unset):
        idtag (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[LongshipError | list[ChargePointAuthorizeGetDto]]
    """

    kwargs = _get_kwargs(
        id=id,
        from_=from_,
        to=to,
        descending=descending,
        status=status,
        search=search,
        skip=skip,
        take=take,
        idtag=idtag,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
    descending: bool | Unset = UNSET,
    status: str | Unset = UNSET,
    search: str | Unset = UNSET,
    skip: int | Unset = UNSET,
    take: int | Unset = UNSET,
    idtag: str | Unset = UNSET,
) -> LongshipError | list[ChargePointAuthorizeGetDto] | None:
    """Get a list of chargepointauthorizations.

     Get a paged list of chargepointauthorizations, taken the filters into account.

    Args:
        id (str):
        from_ (datetime.datetime | Unset):
        to (datetime.datetime | Unset):
        descending (bool | Unset):
        status (str | Unset):
        search (str | Unset):
        skip (int | Unset):
        take (int | Unset):
        idtag (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        LongshipError | list[ChargePointAuthorizeGetDto]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            from_=from_,
            to=to,
            descending=descending,
            status=status,
            search=search,
            skip=skip,
            take=take,
            idtag=idtag,
        )
    ).parsed

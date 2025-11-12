from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_all_locations_accesstype import GetAllLocationsAccesstype
from ...models.get_all_locations_chargerpowertype import GetAllLocationsChargerpowertype
from ...models.get_all_locations_order_by import GetAllLocationsOrderBy
from ...models.location_dto import LocationDto
from ...models.longship_error import LongshipError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    skip: int | Unset = UNSET,
    take: int | Unset = UNSET,
    search: str | Unset = UNSET,
    organizationunitcode: str | Unset = UNSET,
    accesstype: GetAllLocationsAccesstype | Unset = GetAllLocationsAccesstype.PUBLIC,
    chargerpowertype: GetAllLocationsChargerpowertype | Unset = GetAllLocationsChargerpowertype.AC,
    order_by: GetAllLocationsOrderBy | Unset = GetAllLocationsOrderBy.NAME,
    descending: bool | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["skip"] = skip

    params["take"] = take

    params["search"] = search

    params["organizationunitcode"] = organizationunitcode

    json_accesstype: str | Unset = UNSET
    if not isinstance(accesstype, Unset):
        json_accesstype = accesstype.value

    params["accesstype"] = json_accesstype

    json_chargerpowertype: str | Unset = UNSET
    if not isinstance(chargerpowertype, Unset):
        json_chargerpowertype = chargerpowertype.value

    params["chargerpowertype"] = json_chargerpowertype

    json_order_by: str | Unset = UNSET
    if not isinstance(order_by, Unset):
        json_order_by = order_by.value

    params["orderBy"] = json_order_by

    params["descending"] = descending

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/locations",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> LongshipError | list[LocationDto] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemaslocation_dto_array_item_data in _response_200:
            componentsschemaslocation_dto_array_item = LocationDto.from_dict(
                componentsschemaslocation_dto_array_item_data
            )

            response_200.append(componentsschemaslocation_dto_array_item)

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
) -> Response[LongshipError | list[LocationDto]]:
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
    organizationunitcode: str | Unset = UNSET,
    accesstype: GetAllLocationsAccesstype | Unset = GetAllLocationsAccesstype.PUBLIC,
    chargerpowertype: GetAllLocationsChargerpowertype | Unset = GetAllLocationsChargerpowertype.AC,
    order_by: GetAllLocationsOrderBy | Unset = GetAllLocationsOrderBy.NAME,
    descending: bool | Unset = UNSET,
) -> Response[LongshipError | list[LocationDto]]:
    """Get a list of locations.

     This API version is deprecated. Please use v2.

    Args:
        skip (int | Unset):
        take (int | Unset):
        search (str | Unset):
        organizationunitcode (str | Unset):
        accesstype (GetAllLocationsAccesstype | Unset):  Default:
            GetAllLocationsAccesstype.PUBLIC.
        chargerpowertype (GetAllLocationsChargerpowertype | Unset):  Default:
            GetAllLocationsChargerpowertype.AC.
        order_by (GetAllLocationsOrderBy | Unset):  Default: GetAllLocationsOrderBy.NAME.
        descending (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[LongshipError | list[LocationDto]]
    """

    kwargs = _get_kwargs(
        skip=skip,
        take=take,
        search=search,
        organizationunitcode=organizationunitcode,
        accesstype=accesstype,
        chargerpowertype=chargerpowertype,
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
    organizationunitcode: str | Unset = UNSET,
    accesstype: GetAllLocationsAccesstype | Unset = GetAllLocationsAccesstype.PUBLIC,
    chargerpowertype: GetAllLocationsChargerpowertype | Unset = GetAllLocationsChargerpowertype.AC,
    order_by: GetAllLocationsOrderBy | Unset = GetAllLocationsOrderBy.NAME,
    descending: bool | Unset = UNSET,
) -> LongshipError | list[LocationDto] | None:
    """Get a list of locations.

     This API version is deprecated. Please use v2.

    Args:
        skip (int | Unset):
        take (int | Unset):
        search (str | Unset):
        organizationunitcode (str | Unset):
        accesstype (GetAllLocationsAccesstype | Unset):  Default:
            GetAllLocationsAccesstype.PUBLIC.
        chargerpowertype (GetAllLocationsChargerpowertype | Unset):  Default:
            GetAllLocationsChargerpowertype.AC.
        order_by (GetAllLocationsOrderBy | Unset):  Default: GetAllLocationsOrderBy.NAME.
        descending (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        LongshipError | list[LocationDto]
    """

    return sync_detailed(
        client=client,
        skip=skip,
        take=take,
        search=search,
        organizationunitcode=organizationunitcode,
        accesstype=accesstype,
        chargerpowertype=chargerpowertype,
        order_by=order_by,
        descending=descending,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = UNSET,
    take: int | Unset = UNSET,
    search: str | Unset = UNSET,
    organizationunitcode: str | Unset = UNSET,
    accesstype: GetAllLocationsAccesstype | Unset = GetAllLocationsAccesstype.PUBLIC,
    chargerpowertype: GetAllLocationsChargerpowertype | Unset = GetAllLocationsChargerpowertype.AC,
    order_by: GetAllLocationsOrderBy | Unset = GetAllLocationsOrderBy.NAME,
    descending: bool | Unset = UNSET,
) -> Response[LongshipError | list[LocationDto]]:
    """Get a list of locations.

     This API version is deprecated. Please use v2.

    Args:
        skip (int | Unset):
        take (int | Unset):
        search (str | Unset):
        organizationunitcode (str | Unset):
        accesstype (GetAllLocationsAccesstype | Unset):  Default:
            GetAllLocationsAccesstype.PUBLIC.
        chargerpowertype (GetAllLocationsChargerpowertype | Unset):  Default:
            GetAllLocationsChargerpowertype.AC.
        order_by (GetAllLocationsOrderBy | Unset):  Default: GetAllLocationsOrderBy.NAME.
        descending (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[LongshipError | list[LocationDto]]
    """

    kwargs = _get_kwargs(
        skip=skip,
        take=take,
        search=search,
        organizationunitcode=organizationunitcode,
        accesstype=accesstype,
        chargerpowertype=chargerpowertype,
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
    organizationunitcode: str | Unset = UNSET,
    accesstype: GetAllLocationsAccesstype | Unset = GetAllLocationsAccesstype.PUBLIC,
    chargerpowertype: GetAllLocationsChargerpowertype | Unset = GetAllLocationsChargerpowertype.AC,
    order_by: GetAllLocationsOrderBy | Unset = GetAllLocationsOrderBy.NAME,
    descending: bool | Unset = UNSET,
) -> LongshipError | list[LocationDto] | None:
    """Get a list of locations.

     This API version is deprecated. Please use v2.

    Args:
        skip (int | Unset):
        take (int | Unset):
        search (str | Unset):
        organizationunitcode (str | Unset):
        accesstype (GetAllLocationsAccesstype | Unset):  Default:
            GetAllLocationsAccesstype.PUBLIC.
        chargerpowertype (GetAllLocationsChargerpowertype | Unset):  Default:
            GetAllLocationsChargerpowertype.AC.
        order_by (GetAllLocationsOrderBy | Unset):  Default: GetAllLocationsOrderBy.NAME.
        descending (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        LongshipError | list[LocationDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            skip=skip,
            take=take,
            search=search,
            organizationunitcode=organizationunitcode,
            accesstype=accesstype,
            chargerpowertype=chargerpowertype,
            order_by=order_by,
            descending=descending,
        )
    ).parsed

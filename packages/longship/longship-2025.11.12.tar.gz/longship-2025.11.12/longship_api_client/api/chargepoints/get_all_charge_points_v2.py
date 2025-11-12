from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.chargepoint_dto import ChargepointDto
from ...models.get_all_charge_points_v2_accesstype import GetAllChargePointsV2Accesstype
from ...models.get_all_charge_points_v2_chargerpowertype import GetAllChargePointsV2Chargerpowertype
from ...models.get_all_charge_points_v2_operationalstatus import GetAllChargePointsV2Operationalstatus
from ...models.get_all_charge_points_v2_order_by import GetAllChargePointsV2OrderBy
from ...models.get_all_charge_points_v2_search_property import GetAllChargePointsV2SearchProperty
from ...models.longship_error import LongshipError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    skip: int | Unset = UNSET,
    take: int | Unset = UNSET,
    search: str | Unset = UNSET,
    search_property: GetAllChargePointsV2SearchProperty | Unset = GetAllChargePointsV2SearchProperty.CHARGEPOINTID,
    is_online: bool | Unset = UNSET,
    tariff_id: str | Unset = UNSET,
    operationalstatus: GetAllChargePointsV2Operationalstatus | Unset = GetAllChargePointsV2Operationalstatus.AVAILABLE,
    accesstype: GetAllChargePointsV2Accesstype | Unset = GetAllChargePointsV2Accesstype.PUBLIC,
    chargerpowertype: GetAllChargePointsV2Chargerpowertype | Unset = GetAllChargePointsV2Chargerpowertype.AC,
    organizationunitcode: str | Unset = UNSET,
    inactiveonly: bool | Unset = UNSET,
    includenew: bool | Unset = UNSET,
    firmwareversion: str | Unset = UNSET,
    model: str | Unset = UNSET,
    vendor: str | Unset = UNSET,
    order_by: GetAllChargePointsV2OrderBy | Unset = GetAllChargePointsV2OrderBy.NAME,
    descending: bool | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["skip"] = skip

    params["take"] = take

    params["search"] = search

    json_search_property: str | Unset = UNSET
    if not isinstance(search_property, Unset):
        json_search_property = search_property.value

    params["searchProperty"] = json_search_property

    params["isOnline"] = is_online

    params["tariffId"] = tariff_id

    json_operationalstatus: str | Unset = UNSET
    if not isinstance(operationalstatus, Unset):
        json_operationalstatus = operationalstatus.value

    params["operationalstatus"] = json_operationalstatus

    json_accesstype: str | Unset = UNSET
    if not isinstance(accesstype, Unset):
        json_accesstype = accesstype.value

    params["accesstype"] = json_accesstype

    json_chargerpowertype: str | Unset = UNSET
    if not isinstance(chargerpowertype, Unset):
        json_chargerpowertype = chargerpowertype.value

    params["chargerpowertype"] = json_chargerpowertype

    params["organizationunitcode"] = organizationunitcode

    params["inactiveonly"] = inactiveonly

    params["includenew"] = includenew

    params["firmwareversion"] = firmwareversion

    params["model"] = model

    params["vendor"] = vendor

    json_order_by: str | Unset = UNSET
    if not isinstance(order_by, Unset):
        json_order_by = order_by.value

    params["orderBy"] = json_order_by

    params["descending"] = descending

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/chargepoints",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> LongshipError | list[ChargepointDto] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemaschargepoint_dto_array_item_data in _response_200:
            componentsschemaschargepoint_dto_array_item = ChargepointDto.from_dict(
                componentsschemaschargepoint_dto_array_item_data
            )

            response_200.append(componentsschemaschargepoint_dto_array_item)

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
) -> Response[LongshipError | list[ChargepointDto]]:
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
    search_property: GetAllChargePointsV2SearchProperty | Unset = GetAllChargePointsV2SearchProperty.CHARGEPOINTID,
    is_online: bool | Unset = UNSET,
    tariff_id: str | Unset = UNSET,
    operationalstatus: GetAllChargePointsV2Operationalstatus | Unset = GetAllChargePointsV2Operationalstatus.AVAILABLE,
    accesstype: GetAllChargePointsV2Accesstype | Unset = GetAllChargePointsV2Accesstype.PUBLIC,
    chargerpowertype: GetAllChargePointsV2Chargerpowertype | Unset = GetAllChargePointsV2Chargerpowertype.AC,
    organizationunitcode: str | Unset = UNSET,
    inactiveonly: bool | Unset = UNSET,
    includenew: bool | Unset = UNSET,
    firmwareversion: str | Unset = UNSET,
    model: str | Unset = UNSET,
    vendor: str | Unset = UNSET,
    order_by: GetAllChargePointsV2OrderBy | Unset = GetAllChargePointsV2OrderBy.NAME,
    descending: bool | Unset = UNSET,
) -> Response[LongshipError | list[ChargepointDto]]:
    """Get a list of chargepoints.

     Get a list of ChargePoints. This API version supports the searchProperty parameter.

    Args:
        skip (int | Unset):
        take (int | Unset):
        search (str | Unset):
        search_property (GetAllChargePointsV2SearchProperty | Unset):  Default:
            GetAllChargePointsV2SearchProperty.CHARGEPOINTID.
        is_online (bool | Unset):
        tariff_id (str | Unset):
        operationalstatus (GetAllChargePointsV2Operationalstatus | Unset):  Default:
            GetAllChargePointsV2Operationalstatus.AVAILABLE.
        accesstype (GetAllChargePointsV2Accesstype | Unset):  Default:
            GetAllChargePointsV2Accesstype.PUBLIC.
        chargerpowertype (GetAllChargePointsV2Chargerpowertype | Unset):  Default:
            GetAllChargePointsV2Chargerpowertype.AC.
        organizationunitcode (str | Unset):
        inactiveonly (bool | Unset):
        includenew (bool | Unset):
        firmwareversion (str | Unset):
        model (str | Unset):
        vendor (str | Unset):
        order_by (GetAllChargePointsV2OrderBy | Unset):  Default:
            GetAllChargePointsV2OrderBy.NAME.
        descending (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[LongshipError | list[ChargepointDto]]
    """

    kwargs = _get_kwargs(
        skip=skip,
        take=take,
        search=search,
        search_property=search_property,
        is_online=is_online,
        tariff_id=tariff_id,
        operationalstatus=operationalstatus,
        accesstype=accesstype,
        chargerpowertype=chargerpowertype,
        organizationunitcode=organizationunitcode,
        inactiveonly=inactiveonly,
        includenew=includenew,
        firmwareversion=firmwareversion,
        model=model,
        vendor=vendor,
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
    search_property: GetAllChargePointsV2SearchProperty | Unset = GetAllChargePointsV2SearchProperty.CHARGEPOINTID,
    is_online: bool | Unset = UNSET,
    tariff_id: str | Unset = UNSET,
    operationalstatus: GetAllChargePointsV2Operationalstatus | Unset = GetAllChargePointsV2Operationalstatus.AVAILABLE,
    accesstype: GetAllChargePointsV2Accesstype | Unset = GetAllChargePointsV2Accesstype.PUBLIC,
    chargerpowertype: GetAllChargePointsV2Chargerpowertype | Unset = GetAllChargePointsV2Chargerpowertype.AC,
    organizationunitcode: str | Unset = UNSET,
    inactiveonly: bool | Unset = UNSET,
    includenew: bool | Unset = UNSET,
    firmwareversion: str | Unset = UNSET,
    model: str | Unset = UNSET,
    vendor: str | Unset = UNSET,
    order_by: GetAllChargePointsV2OrderBy | Unset = GetAllChargePointsV2OrderBy.NAME,
    descending: bool | Unset = UNSET,
) -> LongshipError | list[ChargepointDto] | None:
    """Get a list of chargepoints.

     Get a list of ChargePoints. This API version supports the searchProperty parameter.

    Args:
        skip (int | Unset):
        take (int | Unset):
        search (str | Unset):
        search_property (GetAllChargePointsV2SearchProperty | Unset):  Default:
            GetAllChargePointsV2SearchProperty.CHARGEPOINTID.
        is_online (bool | Unset):
        tariff_id (str | Unset):
        operationalstatus (GetAllChargePointsV2Operationalstatus | Unset):  Default:
            GetAllChargePointsV2Operationalstatus.AVAILABLE.
        accesstype (GetAllChargePointsV2Accesstype | Unset):  Default:
            GetAllChargePointsV2Accesstype.PUBLIC.
        chargerpowertype (GetAllChargePointsV2Chargerpowertype | Unset):  Default:
            GetAllChargePointsV2Chargerpowertype.AC.
        organizationunitcode (str | Unset):
        inactiveonly (bool | Unset):
        includenew (bool | Unset):
        firmwareversion (str | Unset):
        model (str | Unset):
        vendor (str | Unset):
        order_by (GetAllChargePointsV2OrderBy | Unset):  Default:
            GetAllChargePointsV2OrderBy.NAME.
        descending (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        LongshipError | list[ChargepointDto]
    """

    return sync_detailed(
        client=client,
        skip=skip,
        take=take,
        search=search,
        search_property=search_property,
        is_online=is_online,
        tariff_id=tariff_id,
        operationalstatus=operationalstatus,
        accesstype=accesstype,
        chargerpowertype=chargerpowertype,
        organizationunitcode=organizationunitcode,
        inactiveonly=inactiveonly,
        includenew=includenew,
        firmwareversion=firmwareversion,
        model=model,
        vendor=vendor,
        order_by=order_by,
        descending=descending,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = UNSET,
    take: int | Unset = UNSET,
    search: str | Unset = UNSET,
    search_property: GetAllChargePointsV2SearchProperty | Unset = GetAllChargePointsV2SearchProperty.CHARGEPOINTID,
    is_online: bool | Unset = UNSET,
    tariff_id: str | Unset = UNSET,
    operationalstatus: GetAllChargePointsV2Operationalstatus | Unset = GetAllChargePointsV2Operationalstatus.AVAILABLE,
    accesstype: GetAllChargePointsV2Accesstype | Unset = GetAllChargePointsV2Accesstype.PUBLIC,
    chargerpowertype: GetAllChargePointsV2Chargerpowertype | Unset = GetAllChargePointsV2Chargerpowertype.AC,
    organizationunitcode: str | Unset = UNSET,
    inactiveonly: bool | Unset = UNSET,
    includenew: bool | Unset = UNSET,
    firmwareversion: str | Unset = UNSET,
    model: str | Unset = UNSET,
    vendor: str | Unset = UNSET,
    order_by: GetAllChargePointsV2OrderBy | Unset = GetAllChargePointsV2OrderBy.NAME,
    descending: bool | Unset = UNSET,
) -> Response[LongshipError | list[ChargepointDto]]:
    """Get a list of chargepoints.

     Get a list of ChargePoints. This API version supports the searchProperty parameter.

    Args:
        skip (int | Unset):
        take (int | Unset):
        search (str | Unset):
        search_property (GetAllChargePointsV2SearchProperty | Unset):  Default:
            GetAllChargePointsV2SearchProperty.CHARGEPOINTID.
        is_online (bool | Unset):
        tariff_id (str | Unset):
        operationalstatus (GetAllChargePointsV2Operationalstatus | Unset):  Default:
            GetAllChargePointsV2Operationalstatus.AVAILABLE.
        accesstype (GetAllChargePointsV2Accesstype | Unset):  Default:
            GetAllChargePointsV2Accesstype.PUBLIC.
        chargerpowertype (GetAllChargePointsV2Chargerpowertype | Unset):  Default:
            GetAllChargePointsV2Chargerpowertype.AC.
        organizationunitcode (str | Unset):
        inactiveonly (bool | Unset):
        includenew (bool | Unset):
        firmwareversion (str | Unset):
        model (str | Unset):
        vendor (str | Unset):
        order_by (GetAllChargePointsV2OrderBy | Unset):  Default:
            GetAllChargePointsV2OrderBy.NAME.
        descending (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[LongshipError | list[ChargepointDto]]
    """

    kwargs = _get_kwargs(
        skip=skip,
        take=take,
        search=search,
        search_property=search_property,
        is_online=is_online,
        tariff_id=tariff_id,
        operationalstatus=operationalstatus,
        accesstype=accesstype,
        chargerpowertype=chargerpowertype,
        organizationunitcode=organizationunitcode,
        inactiveonly=inactiveonly,
        includenew=includenew,
        firmwareversion=firmwareversion,
        model=model,
        vendor=vendor,
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
    search_property: GetAllChargePointsV2SearchProperty | Unset = GetAllChargePointsV2SearchProperty.CHARGEPOINTID,
    is_online: bool | Unset = UNSET,
    tariff_id: str | Unset = UNSET,
    operationalstatus: GetAllChargePointsV2Operationalstatus | Unset = GetAllChargePointsV2Operationalstatus.AVAILABLE,
    accesstype: GetAllChargePointsV2Accesstype | Unset = GetAllChargePointsV2Accesstype.PUBLIC,
    chargerpowertype: GetAllChargePointsV2Chargerpowertype | Unset = GetAllChargePointsV2Chargerpowertype.AC,
    organizationunitcode: str | Unset = UNSET,
    inactiveonly: bool | Unset = UNSET,
    includenew: bool | Unset = UNSET,
    firmwareversion: str | Unset = UNSET,
    model: str | Unset = UNSET,
    vendor: str | Unset = UNSET,
    order_by: GetAllChargePointsV2OrderBy | Unset = GetAllChargePointsV2OrderBy.NAME,
    descending: bool | Unset = UNSET,
) -> LongshipError | list[ChargepointDto] | None:
    """Get a list of chargepoints.

     Get a list of ChargePoints. This API version supports the searchProperty parameter.

    Args:
        skip (int | Unset):
        take (int | Unset):
        search (str | Unset):
        search_property (GetAllChargePointsV2SearchProperty | Unset):  Default:
            GetAllChargePointsV2SearchProperty.CHARGEPOINTID.
        is_online (bool | Unset):
        tariff_id (str | Unset):
        operationalstatus (GetAllChargePointsV2Operationalstatus | Unset):  Default:
            GetAllChargePointsV2Operationalstatus.AVAILABLE.
        accesstype (GetAllChargePointsV2Accesstype | Unset):  Default:
            GetAllChargePointsV2Accesstype.PUBLIC.
        chargerpowertype (GetAllChargePointsV2Chargerpowertype | Unset):  Default:
            GetAllChargePointsV2Chargerpowertype.AC.
        organizationunitcode (str | Unset):
        inactiveonly (bool | Unset):
        includenew (bool | Unset):
        firmwareversion (str | Unset):
        model (str | Unset):
        vendor (str | Unset):
        order_by (GetAllChargePointsV2OrderBy | Unset):  Default:
            GetAllChargePointsV2OrderBy.NAME.
        descending (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        LongshipError | list[ChargepointDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            skip=skip,
            take=take,
            search=search,
            search_property=search_property,
            is_online=is_online,
            tariff_id=tariff_id,
            operationalstatus=operationalstatus,
            accesstype=accesstype,
            chargerpowertype=chargerpowertype,
            organizationunitcode=organizationunitcode,
            inactiveonly=inactiveonly,
            includenew=includenew,
            firmwareversion=firmwareversion,
            model=model,
            vendor=vendor,
            order_by=order_by,
            descending=descending,
        )
    ).parsed

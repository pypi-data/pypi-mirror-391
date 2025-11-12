import datetime
from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.cdr_dto import CdrDto
from ...models.get_all_cdrs_order_by import GetAllCdrsOrderBy
from ...models.longship_error import LongshipError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    skip: int | Unset = UNSET,
    take: int | Unset = UNSET,
    search: str | Unset = UNSET,
    providerexclude: str | Unset = UNSET,
    tariff_id: str | Unset = UNSET,
    idtag: str | Unset = UNSET,
    authorizationreferenceid: str | Unset = UNSET,
    providerid: str | Unset = UNSET,
    pricegreaterthen: float | Unset = UNSET,
    pricelessthen: float | Unset = UNSET,
    kwhgreaterthen: float | Unset = UNSET,
    kwhlessthen: float | Unset = UNSET,
    durationinhoursgreaterthen: float | Unset = UNSET,
    durationinhourslessthen: float | Unset = UNSET,
    chargepoint_id: str | Unset = UNSET,
    connector_number: int | Unset = UNSET,
    roamingconnectionid: str | Unset = UNSET,
    organizationunitcode: str | Unset = UNSET,
    local_only: bool | Unset = UNSET,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
    from_last_updated: datetime.datetime | Unset = UNSET,
    to_last_updated: datetime.datetime | Unset = UNSET,
    order_by: GetAllCdrsOrderBy | Unset = GetAllCdrsOrderBy.STARTDATETIME,
    descending: bool | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["skip"] = skip

    params["take"] = take

    params["search"] = search

    params["providerexclude"] = providerexclude

    params["tariffId"] = tariff_id

    params["idtag"] = idtag

    params["authorizationreferenceid"] = authorizationreferenceid

    params["providerid"] = providerid

    params["pricegreaterthen"] = pricegreaterthen

    params["pricelessthen"] = pricelessthen

    params["kwhgreaterthen"] = kwhgreaterthen

    params["kwhlessthen"] = kwhlessthen

    params["durationinhoursgreaterthen"] = durationinhoursgreaterthen

    params["durationinhourslessthen"] = durationinhourslessthen

    params["chargepointId"] = chargepoint_id

    params["connectorNumber"] = connector_number

    params["roamingconnectionid"] = roamingconnectionid

    params["organizationunitcode"] = organizationunitcode

    params["localOnly"] = local_only

    json_from_: str | Unset = UNSET
    if not isinstance(from_, Unset):
        json_from_ = from_.isoformat()
    params["from"] = json_from_

    json_to: str | Unset = UNSET
    if not isinstance(to, Unset):
        json_to = to.isoformat()
    params["to"] = json_to

    json_from_last_updated: str | Unset = UNSET
    if not isinstance(from_last_updated, Unset):
        json_from_last_updated = from_last_updated.isoformat()
    params["fromLastUpdated"] = json_from_last_updated

    json_to_last_updated: str | Unset = UNSET
    if not isinstance(to_last_updated, Unset):
        json_to_last_updated = to_last_updated.isoformat()
    params["toLastUpdated"] = json_to_last_updated

    json_order_by: str | Unset = UNSET
    if not isinstance(order_by, Unset):
        json_order_by = order_by.value

    params["orderBy"] = json_order_by

    params["descending"] = descending

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/cdrs",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> LongshipError | list[CdrDto] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemascdr_dto_array_item_data in _response_200:
            componentsschemascdr_dto_array_item = CdrDto.from_dict(componentsschemascdr_dto_array_item_data)

            response_200.append(componentsschemascdr_dto_array_item)

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
) -> Response[LongshipError | list[CdrDto]]:
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
    tariff_id: str | Unset = UNSET,
    idtag: str | Unset = UNSET,
    authorizationreferenceid: str | Unset = UNSET,
    providerid: str | Unset = UNSET,
    pricegreaterthen: float | Unset = UNSET,
    pricelessthen: float | Unset = UNSET,
    kwhgreaterthen: float | Unset = UNSET,
    kwhlessthen: float | Unset = UNSET,
    durationinhoursgreaterthen: float | Unset = UNSET,
    durationinhourslessthen: float | Unset = UNSET,
    chargepoint_id: str | Unset = UNSET,
    connector_number: int | Unset = UNSET,
    roamingconnectionid: str | Unset = UNSET,
    organizationunitcode: str | Unset = UNSET,
    local_only: bool | Unset = UNSET,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
    from_last_updated: datetime.datetime | Unset = UNSET,
    to_last_updated: datetime.datetime | Unset = UNSET,
    order_by: GetAllCdrsOrderBy | Unset = GetAllCdrsOrderBy.STARTDATETIME,
    descending: bool | Unset = UNSET,
) -> Response[LongshipError | list[CdrDto]]:
    """Get a list of cdrs.

     This API version is deprecated. Please use v2.

    Args:
        skip (int | Unset):
        take (int | Unset):
        search (str | Unset):
        providerexclude (str | Unset):
        tariff_id (str | Unset):
        idtag (str | Unset):
        authorizationreferenceid (str | Unset):
        providerid (str | Unset):
        pricegreaterthen (float | Unset):
        pricelessthen (float | Unset):
        kwhgreaterthen (float | Unset):
        kwhlessthen (float | Unset):
        durationinhoursgreaterthen (float | Unset):
        durationinhourslessthen (float | Unset):
        chargepoint_id (str | Unset):
        connector_number (int | Unset):
        roamingconnectionid (str | Unset):
        organizationunitcode (str | Unset):
        local_only (bool | Unset):
        from_ (datetime.datetime | Unset):
        to (datetime.datetime | Unset):
        from_last_updated (datetime.datetime | Unset):
        to_last_updated (datetime.datetime | Unset):
        order_by (GetAllCdrsOrderBy | Unset):  Default: GetAllCdrsOrderBy.STARTDATETIME.
        descending (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[LongshipError | list[CdrDto]]
    """

    kwargs = _get_kwargs(
        skip=skip,
        take=take,
        search=search,
        providerexclude=providerexclude,
        tariff_id=tariff_id,
        idtag=idtag,
        authorizationreferenceid=authorizationreferenceid,
        providerid=providerid,
        pricegreaterthen=pricegreaterthen,
        pricelessthen=pricelessthen,
        kwhgreaterthen=kwhgreaterthen,
        kwhlessthen=kwhlessthen,
        durationinhoursgreaterthen=durationinhoursgreaterthen,
        durationinhourslessthen=durationinhourslessthen,
        chargepoint_id=chargepoint_id,
        connector_number=connector_number,
        roamingconnectionid=roamingconnectionid,
        organizationunitcode=organizationunitcode,
        local_only=local_only,
        from_=from_,
        to=to,
        from_last_updated=from_last_updated,
        to_last_updated=to_last_updated,
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
    providerexclude: str | Unset = UNSET,
    tariff_id: str | Unset = UNSET,
    idtag: str | Unset = UNSET,
    authorizationreferenceid: str | Unset = UNSET,
    providerid: str | Unset = UNSET,
    pricegreaterthen: float | Unset = UNSET,
    pricelessthen: float | Unset = UNSET,
    kwhgreaterthen: float | Unset = UNSET,
    kwhlessthen: float | Unset = UNSET,
    durationinhoursgreaterthen: float | Unset = UNSET,
    durationinhourslessthen: float | Unset = UNSET,
    chargepoint_id: str | Unset = UNSET,
    connector_number: int | Unset = UNSET,
    roamingconnectionid: str | Unset = UNSET,
    organizationunitcode: str | Unset = UNSET,
    local_only: bool | Unset = UNSET,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
    from_last_updated: datetime.datetime | Unset = UNSET,
    to_last_updated: datetime.datetime | Unset = UNSET,
    order_by: GetAllCdrsOrderBy | Unset = GetAllCdrsOrderBy.STARTDATETIME,
    descending: bool | Unset = UNSET,
) -> LongshipError | list[CdrDto] | None:
    """Get a list of cdrs.

     This API version is deprecated. Please use v2.

    Args:
        skip (int | Unset):
        take (int | Unset):
        search (str | Unset):
        providerexclude (str | Unset):
        tariff_id (str | Unset):
        idtag (str | Unset):
        authorizationreferenceid (str | Unset):
        providerid (str | Unset):
        pricegreaterthen (float | Unset):
        pricelessthen (float | Unset):
        kwhgreaterthen (float | Unset):
        kwhlessthen (float | Unset):
        durationinhoursgreaterthen (float | Unset):
        durationinhourslessthen (float | Unset):
        chargepoint_id (str | Unset):
        connector_number (int | Unset):
        roamingconnectionid (str | Unset):
        organizationunitcode (str | Unset):
        local_only (bool | Unset):
        from_ (datetime.datetime | Unset):
        to (datetime.datetime | Unset):
        from_last_updated (datetime.datetime | Unset):
        to_last_updated (datetime.datetime | Unset):
        order_by (GetAllCdrsOrderBy | Unset):  Default: GetAllCdrsOrderBy.STARTDATETIME.
        descending (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        LongshipError | list[CdrDto]
    """

    return sync_detailed(
        client=client,
        skip=skip,
        take=take,
        search=search,
        providerexclude=providerexclude,
        tariff_id=tariff_id,
        idtag=idtag,
        authorizationreferenceid=authorizationreferenceid,
        providerid=providerid,
        pricegreaterthen=pricegreaterthen,
        pricelessthen=pricelessthen,
        kwhgreaterthen=kwhgreaterthen,
        kwhlessthen=kwhlessthen,
        durationinhoursgreaterthen=durationinhoursgreaterthen,
        durationinhourslessthen=durationinhourslessthen,
        chargepoint_id=chargepoint_id,
        connector_number=connector_number,
        roamingconnectionid=roamingconnectionid,
        organizationunitcode=organizationunitcode,
        local_only=local_only,
        from_=from_,
        to=to,
        from_last_updated=from_last_updated,
        to_last_updated=to_last_updated,
        order_by=order_by,
        descending=descending,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = UNSET,
    take: int | Unset = UNSET,
    search: str | Unset = UNSET,
    providerexclude: str | Unset = UNSET,
    tariff_id: str | Unset = UNSET,
    idtag: str | Unset = UNSET,
    authorizationreferenceid: str | Unset = UNSET,
    providerid: str | Unset = UNSET,
    pricegreaterthen: float | Unset = UNSET,
    pricelessthen: float | Unset = UNSET,
    kwhgreaterthen: float | Unset = UNSET,
    kwhlessthen: float | Unset = UNSET,
    durationinhoursgreaterthen: float | Unset = UNSET,
    durationinhourslessthen: float | Unset = UNSET,
    chargepoint_id: str | Unset = UNSET,
    connector_number: int | Unset = UNSET,
    roamingconnectionid: str | Unset = UNSET,
    organizationunitcode: str | Unset = UNSET,
    local_only: bool | Unset = UNSET,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
    from_last_updated: datetime.datetime | Unset = UNSET,
    to_last_updated: datetime.datetime | Unset = UNSET,
    order_by: GetAllCdrsOrderBy | Unset = GetAllCdrsOrderBy.STARTDATETIME,
    descending: bool | Unset = UNSET,
) -> Response[LongshipError | list[CdrDto]]:
    """Get a list of cdrs.

     This API version is deprecated. Please use v2.

    Args:
        skip (int | Unset):
        take (int | Unset):
        search (str | Unset):
        providerexclude (str | Unset):
        tariff_id (str | Unset):
        idtag (str | Unset):
        authorizationreferenceid (str | Unset):
        providerid (str | Unset):
        pricegreaterthen (float | Unset):
        pricelessthen (float | Unset):
        kwhgreaterthen (float | Unset):
        kwhlessthen (float | Unset):
        durationinhoursgreaterthen (float | Unset):
        durationinhourslessthen (float | Unset):
        chargepoint_id (str | Unset):
        connector_number (int | Unset):
        roamingconnectionid (str | Unset):
        organizationunitcode (str | Unset):
        local_only (bool | Unset):
        from_ (datetime.datetime | Unset):
        to (datetime.datetime | Unset):
        from_last_updated (datetime.datetime | Unset):
        to_last_updated (datetime.datetime | Unset):
        order_by (GetAllCdrsOrderBy | Unset):  Default: GetAllCdrsOrderBy.STARTDATETIME.
        descending (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[LongshipError | list[CdrDto]]
    """

    kwargs = _get_kwargs(
        skip=skip,
        take=take,
        search=search,
        providerexclude=providerexclude,
        tariff_id=tariff_id,
        idtag=idtag,
        authorizationreferenceid=authorizationreferenceid,
        providerid=providerid,
        pricegreaterthen=pricegreaterthen,
        pricelessthen=pricelessthen,
        kwhgreaterthen=kwhgreaterthen,
        kwhlessthen=kwhlessthen,
        durationinhoursgreaterthen=durationinhoursgreaterthen,
        durationinhourslessthen=durationinhourslessthen,
        chargepoint_id=chargepoint_id,
        connector_number=connector_number,
        roamingconnectionid=roamingconnectionid,
        organizationunitcode=organizationunitcode,
        local_only=local_only,
        from_=from_,
        to=to,
        from_last_updated=from_last_updated,
        to_last_updated=to_last_updated,
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
    providerexclude: str | Unset = UNSET,
    tariff_id: str | Unset = UNSET,
    idtag: str | Unset = UNSET,
    authorizationreferenceid: str | Unset = UNSET,
    providerid: str | Unset = UNSET,
    pricegreaterthen: float | Unset = UNSET,
    pricelessthen: float | Unset = UNSET,
    kwhgreaterthen: float | Unset = UNSET,
    kwhlessthen: float | Unset = UNSET,
    durationinhoursgreaterthen: float | Unset = UNSET,
    durationinhourslessthen: float | Unset = UNSET,
    chargepoint_id: str | Unset = UNSET,
    connector_number: int | Unset = UNSET,
    roamingconnectionid: str | Unset = UNSET,
    organizationunitcode: str | Unset = UNSET,
    local_only: bool | Unset = UNSET,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
    from_last_updated: datetime.datetime | Unset = UNSET,
    to_last_updated: datetime.datetime | Unset = UNSET,
    order_by: GetAllCdrsOrderBy | Unset = GetAllCdrsOrderBy.STARTDATETIME,
    descending: bool | Unset = UNSET,
) -> LongshipError | list[CdrDto] | None:
    """Get a list of cdrs.

     This API version is deprecated. Please use v2.

    Args:
        skip (int | Unset):
        take (int | Unset):
        search (str | Unset):
        providerexclude (str | Unset):
        tariff_id (str | Unset):
        idtag (str | Unset):
        authorizationreferenceid (str | Unset):
        providerid (str | Unset):
        pricegreaterthen (float | Unset):
        pricelessthen (float | Unset):
        kwhgreaterthen (float | Unset):
        kwhlessthen (float | Unset):
        durationinhoursgreaterthen (float | Unset):
        durationinhourslessthen (float | Unset):
        chargepoint_id (str | Unset):
        connector_number (int | Unset):
        roamingconnectionid (str | Unset):
        organizationunitcode (str | Unset):
        local_only (bool | Unset):
        from_ (datetime.datetime | Unset):
        to (datetime.datetime | Unset):
        from_last_updated (datetime.datetime | Unset):
        to_last_updated (datetime.datetime | Unset):
        order_by (GetAllCdrsOrderBy | Unset):  Default: GetAllCdrsOrderBy.STARTDATETIME.
        descending (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        LongshipError | list[CdrDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            skip=skip,
            take=take,
            search=search,
            providerexclude=providerexclude,
            tariff_id=tariff_id,
            idtag=idtag,
            authorizationreferenceid=authorizationreferenceid,
            providerid=providerid,
            pricegreaterthen=pricegreaterthen,
            pricelessthen=pricelessthen,
            kwhgreaterthen=kwhgreaterthen,
            kwhlessthen=kwhlessthen,
            durationinhoursgreaterthen=durationinhoursgreaterthen,
            durationinhourslessthen=durationinhourslessthen,
            chargepoint_id=chargepoint_id,
            connector_number=connector_number,
            roamingconnectionid=roamingconnectionid,
            organizationunitcode=organizationunitcode,
            local_only=local_only,
            from_=from_,
            to=to,
            from_last_updated=from_last_updated,
            to_last_updated=to_last_updated,
            order_by=order_by,
            descending=descending,
        )
    ).parsed

import datetime
from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_all_sessions_v2_order_by import GetAllSessionsV2OrderBy
from ...models.get_all_sessions_v2_search_property import GetAllSessionsV2SearchProperty
from ...models.longship_error import LongshipError
from ...models.session_dto import SessionDto
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    skip: int | Unset = UNSET,
    take: int | Unset = UNSET,
    search: str | Unset = UNSET,
    search_property: GetAllSessionsV2SearchProperty | Unset = GetAllSessionsV2SearchProperty.SESSIONID,
    connector_number: int | Unset = UNSET,
    chargepoint_id: str | Unset = UNSET,
    running_only: bool | Unset = UNSET,
    completed_only: bool | Unset = UNSET,
    suspicious_only: bool | Unset = UNSET,
    rejected_only: bool | Unset = UNSET,
    local_only: bool | Unset = UNSET,
    unauthorized_only: bool | Unset = UNSET,
    roamingconnectionid: str | Unset = UNSET,
    organizationunitcode: str | Unset = UNSET,
    tariff_id: str | Unset = UNSET,
    pricegreaterthen: float | Unset = UNSET,
    pricelessthen: float | Unset = UNSET,
    kwhgreaterthen: float | Unset = UNSET,
    kwhlessthen: float | Unset = UNSET,
    contractid: str | Unset = UNSET,
    providerid: str | Unset = UNSET,
    authorizationreferenceid: str | Unset = UNSET,
    transaction_id: str | Unset = UNSET,
    idtag: str | Unset = UNSET,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
    from_last_updated: datetime.datetime | Unset = UNSET,
    to_last_updated: datetime.datetime | Unset = UNSET,
    order_by: GetAllSessionsV2OrderBy | Unset = GetAllSessionsV2OrderBy.START,
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

    params["connectorNumber"] = connector_number

    params["chargepointId"] = chargepoint_id

    params["runningOnly"] = running_only

    params["completedOnly"] = completed_only

    params["suspiciousOnly"] = suspicious_only

    params["rejectedOnly"] = rejected_only

    params["localOnly"] = local_only

    params["unauthorizedOnly"] = unauthorized_only

    params["roamingconnectionid"] = roamingconnectionid

    params["organizationunitcode"] = organizationunitcode

    params["tariffId"] = tariff_id

    params["pricegreaterthen"] = pricegreaterthen

    params["pricelessthen"] = pricelessthen

    params["kwhgreaterthen"] = kwhgreaterthen

    params["kwhlessthen"] = kwhlessthen

    params["contractid"] = contractid

    params["providerid"] = providerid

    params["authorizationreferenceid"] = authorizationreferenceid

    params["transactionId"] = transaction_id

    params["idtag"] = idtag

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
        "url": "/v2/sessions",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> LongshipError | list[SessionDto] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemassession_dto_array_item_data in _response_200:
            componentsschemassession_dto_array_item = SessionDto.from_dict(componentsschemassession_dto_array_item_data)

            response_200.append(componentsschemassession_dto_array_item)

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
) -> Response[LongshipError | list[SessionDto]]:
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
    search_property: GetAllSessionsV2SearchProperty | Unset = GetAllSessionsV2SearchProperty.SESSIONID,
    connector_number: int | Unset = UNSET,
    chargepoint_id: str | Unset = UNSET,
    running_only: bool | Unset = UNSET,
    completed_only: bool | Unset = UNSET,
    suspicious_only: bool | Unset = UNSET,
    rejected_only: bool | Unset = UNSET,
    local_only: bool | Unset = UNSET,
    unauthorized_only: bool | Unset = UNSET,
    roamingconnectionid: str | Unset = UNSET,
    organizationunitcode: str | Unset = UNSET,
    tariff_id: str | Unset = UNSET,
    pricegreaterthen: float | Unset = UNSET,
    pricelessthen: float | Unset = UNSET,
    kwhgreaterthen: float | Unset = UNSET,
    kwhlessthen: float | Unset = UNSET,
    contractid: str | Unset = UNSET,
    providerid: str | Unset = UNSET,
    authorizationreferenceid: str | Unset = UNSET,
    transaction_id: str | Unset = UNSET,
    idtag: str | Unset = UNSET,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
    from_last_updated: datetime.datetime | Unset = UNSET,
    to_last_updated: datetime.datetime | Unset = UNSET,
    order_by: GetAllSessionsV2OrderBy | Unset = GetAllSessionsV2OrderBy.START,
    descending: bool | Unset = UNSET,
) -> Response[LongshipError | list[SessionDto]]:
    """Get a list of sessions.

     Get a paged list of sessions, taken the filters into account.

    Args:
        skip (int | Unset):
        take (int | Unset):
        search (str | Unset):
        search_property (GetAllSessionsV2SearchProperty | Unset):  Default:
            GetAllSessionsV2SearchProperty.SESSIONID.
        connector_number (int | Unset):
        chargepoint_id (str | Unset):
        running_only (bool | Unset):
        completed_only (bool | Unset):
        suspicious_only (bool | Unset):
        rejected_only (bool | Unset):
        local_only (bool | Unset):
        unauthorized_only (bool | Unset):
        roamingconnectionid (str | Unset):
        organizationunitcode (str | Unset):
        tariff_id (str | Unset):
        pricegreaterthen (float | Unset):
        pricelessthen (float | Unset):
        kwhgreaterthen (float | Unset):
        kwhlessthen (float | Unset):
        contractid (str | Unset):
        providerid (str | Unset):
        authorizationreferenceid (str | Unset):
        transaction_id (str | Unset):
        idtag (str | Unset):
        from_ (datetime.datetime | Unset):
        to (datetime.datetime | Unset):
        from_last_updated (datetime.datetime | Unset):
        to_last_updated (datetime.datetime | Unset):
        order_by (GetAllSessionsV2OrderBy | Unset):  Default: GetAllSessionsV2OrderBy.START.
        descending (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[LongshipError | list[SessionDto]]
    """

    kwargs = _get_kwargs(
        skip=skip,
        take=take,
        search=search,
        search_property=search_property,
        connector_number=connector_number,
        chargepoint_id=chargepoint_id,
        running_only=running_only,
        completed_only=completed_only,
        suspicious_only=suspicious_only,
        rejected_only=rejected_only,
        local_only=local_only,
        unauthorized_only=unauthorized_only,
        roamingconnectionid=roamingconnectionid,
        organizationunitcode=organizationunitcode,
        tariff_id=tariff_id,
        pricegreaterthen=pricegreaterthen,
        pricelessthen=pricelessthen,
        kwhgreaterthen=kwhgreaterthen,
        kwhlessthen=kwhlessthen,
        contractid=contractid,
        providerid=providerid,
        authorizationreferenceid=authorizationreferenceid,
        transaction_id=transaction_id,
        idtag=idtag,
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
    search_property: GetAllSessionsV2SearchProperty | Unset = GetAllSessionsV2SearchProperty.SESSIONID,
    connector_number: int | Unset = UNSET,
    chargepoint_id: str | Unset = UNSET,
    running_only: bool | Unset = UNSET,
    completed_only: bool | Unset = UNSET,
    suspicious_only: bool | Unset = UNSET,
    rejected_only: bool | Unset = UNSET,
    local_only: bool | Unset = UNSET,
    unauthorized_only: bool | Unset = UNSET,
    roamingconnectionid: str | Unset = UNSET,
    organizationunitcode: str | Unset = UNSET,
    tariff_id: str | Unset = UNSET,
    pricegreaterthen: float | Unset = UNSET,
    pricelessthen: float | Unset = UNSET,
    kwhgreaterthen: float | Unset = UNSET,
    kwhlessthen: float | Unset = UNSET,
    contractid: str | Unset = UNSET,
    providerid: str | Unset = UNSET,
    authorizationreferenceid: str | Unset = UNSET,
    transaction_id: str | Unset = UNSET,
    idtag: str | Unset = UNSET,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
    from_last_updated: datetime.datetime | Unset = UNSET,
    to_last_updated: datetime.datetime | Unset = UNSET,
    order_by: GetAllSessionsV2OrderBy | Unset = GetAllSessionsV2OrderBy.START,
    descending: bool | Unset = UNSET,
) -> LongshipError | list[SessionDto] | None:
    """Get a list of sessions.

     Get a paged list of sessions, taken the filters into account.

    Args:
        skip (int | Unset):
        take (int | Unset):
        search (str | Unset):
        search_property (GetAllSessionsV2SearchProperty | Unset):  Default:
            GetAllSessionsV2SearchProperty.SESSIONID.
        connector_number (int | Unset):
        chargepoint_id (str | Unset):
        running_only (bool | Unset):
        completed_only (bool | Unset):
        suspicious_only (bool | Unset):
        rejected_only (bool | Unset):
        local_only (bool | Unset):
        unauthorized_only (bool | Unset):
        roamingconnectionid (str | Unset):
        organizationunitcode (str | Unset):
        tariff_id (str | Unset):
        pricegreaterthen (float | Unset):
        pricelessthen (float | Unset):
        kwhgreaterthen (float | Unset):
        kwhlessthen (float | Unset):
        contractid (str | Unset):
        providerid (str | Unset):
        authorizationreferenceid (str | Unset):
        transaction_id (str | Unset):
        idtag (str | Unset):
        from_ (datetime.datetime | Unset):
        to (datetime.datetime | Unset):
        from_last_updated (datetime.datetime | Unset):
        to_last_updated (datetime.datetime | Unset):
        order_by (GetAllSessionsV2OrderBy | Unset):  Default: GetAllSessionsV2OrderBy.START.
        descending (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        LongshipError | list[SessionDto]
    """

    return sync_detailed(
        client=client,
        skip=skip,
        take=take,
        search=search,
        search_property=search_property,
        connector_number=connector_number,
        chargepoint_id=chargepoint_id,
        running_only=running_only,
        completed_only=completed_only,
        suspicious_only=suspicious_only,
        rejected_only=rejected_only,
        local_only=local_only,
        unauthorized_only=unauthorized_only,
        roamingconnectionid=roamingconnectionid,
        organizationunitcode=organizationunitcode,
        tariff_id=tariff_id,
        pricegreaterthen=pricegreaterthen,
        pricelessthen=pricelessthen,
        kwhgreaterthen=kwhgreaterthen,
        kwhlessthen=kwhlessthen,
        contractid=contractid,
        providerid=providerid,
        authorizationreferenceid=authorizationreferenceid,
        transaction_id=transaction_id,
        idtag=idtag,
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
    search_property: GetAllSessionsV2SearchProperty | Unset = GetAllSessionsV2SearchProperty.SESSIONID,
    connector_number: int | Unset = UNSET,
    chargepoint_id: str | Unset = UNSET,
    running_only: bool | Unset = UNSET,
    completed_only: bool | Unset = UNSET,
    suspicious_only: bool | Unset = UNSET,
    rejected_only: bool | Unset = UNSET,
    local_only: bool | Unset = UNSET,
    unauthorized_only: bool | Unset = UNSET,
    roamingconnectionid: str | Unset = UNSET,
    organizationunitcode: str | Unset = UNSET,
    tariff_id: str | Unset = UNSET,
    pricegreaterthen: float | Unset = UNSET,
    pricelessthen: float | Unset = UNSET,
    kwhgreaterthen: float | Unset = UNSET,
    kwhlessthen: float | Unset = UNSET,
    contractid: str | Unset = UNSET,
    providerid: str | Unset = UNSET,
    authorizationreferenceid: str | Unset = UNSET,
    transaction_id: str | Unset = UNSET,
    idtag: str | Unset = UNSET,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
    from_last_updated: datetime.datetime | Unset = UNSET,
    to_last_updated: datetime.datetime | Unset = UNSET,
    order_by: GetAllSessionsV2OrderBy | Unset = GetAllSessionsV2OrderBy.START,
    descending: bool | Unset = UNSET,
) -> Response[LongshipError | list[SessionDto]]:
    """Get a list of sessions.

     Get a paged list of sessions, taken the filters into account.

    Args:
        skip (int | Unset):
        take (int | Unset):
        search (str | Unset):
        search_property (GetAllSessionsV2SearchProperty | Unset):  Default:
            GetAllSessionsV2SearchProperty.SESSIONID.
        connector_number (int | Unset):
        chargepoint_id (str | Unset):
        running_only (bool | Unset):
        completed_only (bool | Unset):
        suspicious_only (bool | Unset):
        rejected_only (bool | Unset):
        local_only (bool | Unset):
        unauthorized_only (bool | Unset):
        roamingconnectionid (str | Unset):
        organizationunitcode (str | Unset):
        tariff_id (str | Unset):
        pricegreaterthen (float | Unset):
        pricelessthen (float | Unset):
        kwhgreaterthen (float | Unset):
        kwhlessthen (float | Unset):
        contractid (str | Unset):
        providerid (str | Unset):
        authorizationreferenceid (str | Unset):
        transaction_id (str | Unset):
        idtag (str | Unset):
        from_ (datetime.datetime | Unset):
        to (datetime.datetime | Unset):
        from_last_updated (datetime.datetime | Unset):
        to_last_updated (datetime.datetime | Unset):
        order_by (GetAllSessionsV2OrderBy | Unset):  Default: GetAllSessionsV2OrderBy.START.
        descending (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[LongshipError | list[SessionDto]]
    """

    kwargs = _get_kwargs(
        skip=skip,
        take=take,
        search=search,
        search_property=search_property,
        connector_number=connector_number,
        chargepoint_id=chargepoint_id,
        running_only=running_only,
        completed_only=completed_only,
        suspicious_only=suspicious_only,
        rejected_only=rejected_only,
        local_only=local_only,
        unauthorized_only=unauthorized_only,
        roamingconnectionid=roamingconnectionid,
        organizationunitcode=organizationunitcode,
        tariff_id=tariff_id,
        pricegreaterthen=pricegreaterthen,
        pricelessthen=pricelessthen,
        kwhgreaterthen=kwhgreaterthen,
        kwhlessthen=kwhlessthen,
        contractid=contractid,
        providerid=providerid,
        authorizationreferenceid=authorizationreferenceid,
        transaction_id=transaction_id,
        idtag=idtag,
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
    search_property: GetAllSessionsV2SearchProperty | Unset = GetAllSessionsV2SearchProperty.SESSIONID,
    connector_number: int | Unset = UNSET,
    chargepoint_id: str | Unset = UNSET,
    running_only: bool | Unset = UNSET,
    completed_only: bool | Unset = UNSET,
    suspicious_only: bool | Unset = UNSET,
    rejected_only: bool | Unset = UNSET,
    local_only: bool | Unset = UNSET,
    unauthorized_only: bool | Unset = UNSET,
    roamingconnectionid: str | Unset = UNSET,
    organizationunitcode: str | Unset = UNSET,
    tariff_id: str | Unset = UNSET,
    pricegreaterthen: float | Unset = UNSET,
    pricelessthen: float | Unset = UNSET,
    kwhgreaterthen: float | Unset = UNSET,
    kwhlessthen: float | Unset = UNSET,
    contractid: str | Unset = UNSET,
    providerid: str | Unset = UNSET,
    authorizationreferenceid: str | Unset = UNSET,
    transaction_id: str | Unset = UNSET,
    idtag: str | Unset = UNSET,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
    from_last_updated: datetime.datetime | Unset = UNSET,
    to_last_updated: datetime.datetime | Unset = UNSET,
    order_by: GetAllSessionsV2OrderBy | Unset = GetAllSessionsV2OrderBy.START,
    descending: bool | Unset = UNSET,
) -> LongshipError | list[SessionDto] | None:
    """Get a list of sessions.

     Get a paged list of sessions, taken the filters into account.

    Args:
        skip (int | Unset):
        take (int | Unset):
        search (str | Unset):
        search_property (GetAllSessionsV2SearchProperty | Unset):  Default:
            GetAllSessionsV2SearchProperty.SESSIONID.
        connector_number (int | Unset):
        chargepoint_id (str | Unset):
        running_only (bool | Unset):
        completed_only (bool | Unset):
        suspicious_only (bool | Unset):
        rejected_only (bool | Unset):
        local_only (bool | Unset):
        unauthorized_only (bool | Unset):
        roamingconnectionid (str | Unset):
        organizationunitcode (str | Unset):
        tariff_id (str | Unset):
        pricegreaterthen (float | Unset):
        pricelessthen (float | Unset):
        kwhgreaterthen (float | Unset):
        kwhlessthen (float | Unset):
        contractid (str | Unset):
        providerid (str | Unset):
        authorizationreferenceid (str | Unset):
        transaction_id (str | Unset):
        idtag (str | Unset):
        from_ (datetime.datetime | Unset):
        to (datetime.datetime | Unset):
        from_last_updated (datetime.datetime | Unset):
        to_last_updated (datetime.datetime | Unset):
        order_by (GetAllSessionsV2OrderBy | Unset):  Default: GetAllSessionsV2OrderBy.START.
        descending (bool | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        LongshipError | list[SessionDto]
    """

    return (
        await asyncio_detailed(
            client=client,
            skip=skip,
            take=take,
            search=search,
            search_property=search_property,
            connector_number=connector_number,
            chargepoint_id=chargepoint_id,
            running_only=running_only,
            completed_only=completed_only,
            suspicious_only=suspicious_only,
            rejected_only=rejected_only,
            local_only=local_only,
            unauthorized_only=unauthorized_only,
            roamingconnectionid=roamingconnectionid,
            organizationunitcode=organizationunitcode,
            tariff_id=tariff_id,
            pricegreaterthen=pricegreaterthen,
            pricelessthen=pricelessthen,
            kwhgreaterthen=kwhgreaterthen,
            kwhlessthen=kwhlessthen,
            contractid=contractid,
            providerid=providerid,
            authorizationreferenceid=authorizationreferenceid,
            transaction_id=transaction_id,
            idtag=idtag,
            from_=from_,
            to=to,
            from_last_updated=from_last_updated,
            to_last_updated=to_last_updated,
            order_by=order_by,
            descending=descending,
        )
    ).parsed

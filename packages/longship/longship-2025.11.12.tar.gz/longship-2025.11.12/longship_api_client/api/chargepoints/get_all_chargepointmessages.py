import datetime
from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.longship_error import LongshipError
from ...models.message_log_dto import MessageLogDto
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: str,
    *,
    skip: int | Unset = UNSET,
    take: int | Unset = UNSET,
    search: str | Unset = UNSET,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
    transaction_id: str | Unset = UNSET,
    response_only: bool | Unset = UNSET,
    request_only: bool | Unset = UNSET,
    charger_to_cpo_only: bool | Unset = UNSET,
    cpo_to_charger_only: bool | Unset = UNSET,
    message_id: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["skip"] = skip

    params["take"] = take

    params["search"] = search

    json_from_: str | Unset = UNSET
    if not isinstance(from_, Unset):
        json_from_ = from_.isoformat()
    params["from"] = json_from_

    json_to: str | Unset = UNSET
    if not isinstance(to, Unset):
        json_to = to.isoformat()
    params["to"] = json_to

    params["transactionId"] = transaction_id

    params["responseOnly"] = response_only

    params["requestOnly"] = request_only

    params["chargerToCpoOnly"] = charger_to_cpo_only

    params["cpoToChargerOnly"] = cpo_to_charger_only

    params["messageId"] = message_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/chargepoints/{id}/messages",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> LongshipError | list[MessageLogDto] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemasmessage_log_dto_array_item_data in _response_200:
            componentsschemasmessage_log_dto_array_item = MessageLogDto.from_dict(
                componentsschemasmessage_log_dto_array_item_data
            )

            response_200.append(componentsschemasmessage_log_dto_array_item)

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
) -> Response[LongshipError | list[MessageLogDto]]:
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
    skip: int | Unset = UNSET,
    take: int | Unset = UNSET,
    search: str | Unset = UNSET,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
    transaction_id: str | Unset = UNSET,
    response_only: bool | Unset = UNSET,
    request_only: bool | Unset = UNSET,
    charger_to_cpo_only: bool | Unset = UNSET,
    cpo_to_charger_only: bool | Unset = UNSET,
    message_id: str | Unset = UNSET,
) -> Response[LongshipError | list[MessageLogDto]]:
    """Get a list of chargepointmessages.

     Get a paged list of chargepointmessages, taken the filters into account.

    Args:
        id (str):
        skip (int | Unset):
        take (int | Unset):
        search (str | Unset):
        from_ (datetime.datetime | Unset):
        to (datetime.datetime | Unset):
        transaction_id (str | Unset):
        response_only (bool | Unset):
        request_only (bool | Unset):
        charger_to_cpo_only (bool | Unset):
        cpo_to_charger_only (bool | Unset):
        message_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[LongshipError | list[MessageLogDto]]
    """

    kwargs = _get_kwargs(
        id=id,
        skip=skip,
        take=take,
        search=search,
        from_=from_,
        to=to,
        transaction_id=transaction_id,
        response_only=response_only,
        request_only=request_only,
        charger_to_cpo_only=charger_to_cpo_only,
        cpo_to_charger_only=cpo_to_charger_only,
        message_id=message_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = UNSET,
    take: int | Unset = UNSET,
    search: str | Unset = UNSET,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
    transaction_id: str | Unset = UNSET,
    response_only: bool | Unset = UNSET,
    request_only: bool | Unset = UNSET,
    charger_to_cpo_only: bool | Unset = UNSET,
    cpo_to_charger_only: bool | Unset = UNSET,
    message_id: str | Unset = UNSET,
) -> LongshipError | list[MessageLogDto] | None:
    """Get a list of chargepointmessages.

     Get a paged list of chargepointmessages, taken the filters into account.

    Args:
        id (str):
        skip (int | Unset):
        take (int | Unset):
        search (str | Unset):
        from_ (datetime.datetime | Unset):
        to (datetime.datetime | Unset):
        transaction_id (str | Unset):
        response_only (bool | Unset):
        request_only (bool | Unset):
        charger_to_cpo_only (bool | Unset):
        cpo_to_charger_only (bool | Unset):
        message_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        LongshipError | list[MessageLogDto]
    """

    return sync_detailed(
        id=id,
        client=client,
        skip=skip,
        take=take,
        search=search,
        from_=from_,
        to=to,
        transaction_id=transaction_id,
        response_only=response_only,
        request_only=request_only,
        charger_to_cpo_only=charger_to_cpo_only,
        cpo_to_charger_only=cpo_to_charger_only,
        message_id=message_id,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = UNSET,
    take: int | Unset = UNSET,
    search: str | Unset = UNSET,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
    transaction_id: str | Unset = UNSET,
    response_only: bool | Unset = UNSET,
    request_only: bool | Unset = UNSET,
    charger_to_cpo_only: bool | Unset = UNSET,
    cpo_to_charger_only: bool | Unset = UNSET,
    message_id: str | Unset = UNSET,
) -> Response[LongshipError | list[MessageLogDto]]:
    """Get a list of chargepointmessages.

     Get a paged list of chargepointmessages, taken the filters into account.

    Args:
        id (str):
        skip (int | Unset):
        take (int | Unset):
        search (str | Unset):
        from_ (datetime.datetime | Unset):
        to (datetime.datetime | Unset):
        transaction_id (str | Unset):
        response_only (bool | Unset):
        request_only (bool | Unset):
        charger_to_cpo_only (bool | Unset):
        cpo_to_charger_only (bool | Unset):
        message_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[LongshipError | list[MessageLogDto]]
    """

    kwargs = _get_kwargs(
        id=id,
        skip=skip,
        take=take,
        search=search,
        from_=from_,
        to=to,
        transaction_id=transaction_id,
        response_only=response_only,
        request_only=request_only,
        charger_to_cpo_only=charger_to_cpo_only,
        cpo_to_charger_only=cpo_to_charger_only,
        message_id=message_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = UNSET,
    take: int | Unset = UNSET,
    search: str | Unset = UNSET,
    from_: datetime.datetime | Unset = UNSET,
    to: datetime.datetime | Unset = UNSET,
    transaction_id: str | Unset = UNSET,
    response_only: bool | Unset = UNSET,
    request_only: bool | Unset = UNSET,
    charger_to_cpo_only: bool | Unset = UNSET,
    cpo_to_charger_only: bool | Unset = UNSET,
    message_id: str | Unset = UNSET,
) -> LongshipError | list[MessageLogDto] | None:
    """Get a list of chargepointmessages.

     Get a paged list of chargepointmessages, taken the filters into account.

    Args:
        id (str):
        skip (int | Unset):
        take (int | Unset):
        search (str | Unset):
        from_ (datetime.datetime | Unset):
        to (datetime.datetime | Unset):
        transaction_id (str | Unset):
        response_only (bool | Unset):
        request_only (bool | Unset):
        charger_to_cpo_only (bool | Unset):
        cpo_to_charger_only (bool | Unset):
        message_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        LongshipError | list[MessageLogDto]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            skip=skip,
            take=take,
            search=search,
            from_=from_,
            to=to,
            transaction_id=transaction_id,
            response_only=response_only,
            request_only=request_only,
            charger_to_cpo_only=charger_to_cpo_only,
            cpo_to_charger_only=cpo_to_charger_only,
            message_id=message_id,
        )
    ).parsed

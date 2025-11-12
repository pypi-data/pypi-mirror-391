from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.local_token_group_token_get_dto import LocalTokenGroupTokenGetDto


T = TypeVar("T", bound="LocalTokenGroupGetDto")


@_attrs_define
class LocalTokenGroupGetDto:
    """
    Attributes:
        id (str | Unset):
        oucode (str | Unset):
        token_group_name (str | Unset):
        target_ou_codes (list[str] | Unset):
        tokens (list[LocalTokenGroupTokenGetDto] | Unset):
        target_chargepoint_ids (list[str] | Unset):
        override_tariff_id (str | Unset):
        created (datetime.datetime | Unset):
        updated (datetime.datetime | Unset):
        is_prefix (bool | Unset):
    """

    id: str | Unset = UNSET
    oucode: str | Unset = UNSET
    token_group_name: str | Unset = UNSET
    target_ou_codes: list[str] | Unset = UNSET
    tokens: list[LocalTokenGroupTokenGetDto] | Unset = UNSET
    target_chargepoint_ids: list[str] | Unset = UNSET
    override_tariff_id: str | Unset = UNSET
    created: datetime.datetime | Unset = UNSET
    updated: datetime.datetime | Unset = UNSET
    is_prefix: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        oucode = self.oucode

        token_group_name = self.token_group_name

        target_ou_codes: list[str] | Unset = UNSET
        if not isinstance(self.target_ou_codes, Unset):
            target_ou_codes = self.target_ou_codes

        tokens: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.tokens, Unset):
            tokens = []
            for tokens_item_data in self.tokens:
                tokens_item = tokens_item_data.to_dict()
                tokens.append(tokens_item)

        target_chargepoint_ids: list[str] | Unset = UNSET
        if not isinstance(self.target_chargepoint_ids, Unset):
            target_chargepoint_ids = self.target_chargepoint_ids

        override_tariff_id = self.override_tariff_id

        created: str | Unset = UNSET
        if not isinstance(self.created, Unset):
            created = self.created.isoformat()

        updated: str | Unset = UNSET
        if not isinstance(self.updated, Unset):
            updated = self.updated.isoformat()

        is_prefix = self.is_prefix

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if oucode is not UNSET:
            field_dict["oucode"] = oucode
        if token_group_name is not UNSET:
            field_dict["tokenGroupName"] = token_group_name
        if target_ou_codes is not UNSET:
            field_dict["targetOUCodes"] = target_ou_codes
        if tokens is not UNSET:
            field_dict["tokens"] = tokens
        if target_chargepoint_ids is not UNSET:
            field_dict["targetChargepointIds"] = target_chargepoint_ids
        if override_tariff_id is not UNSET:
            field_dict["overrideTariffId"] = override_tariff_id
        if created is not UNSET:
            field_dict["created"] = created
        if updated is not UNSET:
            field_dict["updated"] = updated
        if is_prefix is not UNSET:
            field_dict["isPrefix"] = is_prefix

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.local_token_group_token_get_dto import LocalTokenGroupTokenGetDto

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        oucode = d.pop("oucode", UNSET)

        token_group_name = d.pop("tokenGroupName", UNSET)

        target_ou_codes = cast(list[str], d.pop("targetOUCodes", UNSET))

        tokens = []
        _tokens = d.pop("tokens", UNSET)
        for tokens_item_data in _tokens or []:
            tokens_item = LocalTokenGroupTokenGetDto.from_dict(tokens_item_data)

            tokens.append(tokens_item)

        target_chargepoint_ids = cast(list[str], d.pop("targetChargepointIds", UNSET))

        override_tariff_id = d.pop("overrideTariffId", UNSET)

        _created = d.pop("created", UNSET)
        created: datetime.datetime | Unset
        if isinstance(_created, Unset) or _created is None:
            created = UNSET
        else:
            created = isoparse(_created)

        _updated = d.pop("updated", UNSET)
        updated: datetime.datetime | Unset
        if isinstance(_updated, Unset) or _updated is None:
            updated = UNSET
        else:
            updated = isoparse(_updated)

        is_prefix = d.pop("isPrefix", UNSET)

        local_token_group_get_dto = cls(
            id=id,
            oucode=oucode,
            token_group_name=token_group_name,
            target_ou_codes=target_ou_codes,
            tokens=tokens,
            target_chargepoint_ids=target_chargepoint_ids,
            override_tariff_id=override_tariff_id,
            created=created,
            updated=updated,
            is_prefix=is_prefix,
        )

        local_token_group_get_dto.additional_properties = d
        return local_token_group_get_dto

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

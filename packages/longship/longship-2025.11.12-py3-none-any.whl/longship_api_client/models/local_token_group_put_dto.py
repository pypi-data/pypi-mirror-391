from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.local_token_group_token_put_dto import LocalTokenGroupTokenPutDto


T = TypeVar("T", bound="LocalTokenGroupPutDto")


@_attrs_define
class LocalTokenGroupPutDto:
    """
    Attributes:
        oucode (str | Unset):
        token_group_name (str | Unset):
        target_ou_codes (list[str] | Unset):
        override_tariff_id (str | Unset):
        tokens (list[LocalTokenGroupTokenPutDto] | Unset):
        target_chargepoint_ids (list[str] | Unset):
        is_prefix (bool | Unset):
    """

    oucode: str | Unset = UNSET
    token_group_name: str | Unset = UNSET
    target_ou_codes: list[str] | Unset = UNSET
    override_tariff_id: str | Unset = UNSET
    tokens: list[LocalTokenGroupTokenPutDto] | Unset = UNSET
    target_chargepoint_ids: list[str] | Unset = UNSET
    is_prefix: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        oucode = self.oucode

        token_group_name = self.token_group_name

        target_ou_codes: list[str] | Unset = UNSET
        if not isinstance(self.target_ou_codes, Unset):
            target_ou_codes = self.target_ou_codes

        override_tariff_id = self.override_tariff_id

        tokens: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.tokens, Unset):
            tokens = []
            for tokens_item_data in self.tokens:
                tokens_item = tokens_item_data.to_dict()
                tokens.append(tokens_item)

        target_chargepoint_ids: list[str] | Unset = UNSET
        if not isinstance(self.target_chargepoint_ids, Unset):
            target_chargepoint_ids = self.target_chargepoint_ids

        is_prefix = self.is_prefix

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if oucode is not UNSET:
            field_dict["oucode"] = oucode
        if token_group_name is not UNSET:
            field_dict["tokenGroupName"] = token_group_name
        if target_ou_codes is not UNSET:
            field_dict["targetOUCodes"] = target_ou_codes
        if override_tariff_id is not UNSET:
            field_dict["overrideTariffId"] = override_tariff_id
        if tokens is not UNSET:
            field_dict["tokens"] = tokens
        if target_chargepoint_ids is not UNSET:
            field_dict["targetChargepointIds"] = target_chargepoint_ids
        if is_prefix is not UNSET:
            field_dict["isPrefix"] = is_prefix

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.local_token_group_token_put_dto import LocalTokenGroupTokenPutDto

        d = dict(src_dict)
        oucode = d.pop("oucode", UNSET)

        token_group_name = d.pop("tokenGroupName", UNSET)

        target_ou_codes = cast(list[str], d.pop("targetOUCodes", UNSET))

        override_tariff_id = d.pop("overrideTariffId", UNSET)

        tokens = []
        _tokens = d.pop("tokens", UNSET)
        for tokens_item_data in _tokens or []:
            tokens_item = LocalTokenGroupTokenPutDto.from_dict(tokens_item_data)

            tokens.append(tokens_item)

        target_chargepoint_ids = cast(list[str], d.pop("targetChargepointIds", UNSET))

        is_prefix = d.pop("isPrefix", UNSET)

        local_token_group_put_dto = cls(
            oucode=oucode,
            token_group_name=token_group_name,
            target_ou_codes=target_ou_codes,
            override_tariff_id=override_tariff_id,
            tokens=tokens,
            target_chargepoint_ids=target_chargepoint_ids,
            is_prefix=is_prefix,
        )

        local_token_group_put_dto.additional_properties = d
        return local_token_group_put_dto

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

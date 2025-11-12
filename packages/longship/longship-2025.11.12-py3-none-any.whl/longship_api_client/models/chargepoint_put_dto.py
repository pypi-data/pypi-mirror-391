from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChargepointPutDto")


@_attrs_define
class ChargepointPutDto:
    """
    Attributes:
        display_name (str | Unset):
        roaming_name (str | Unset):
        allow_any_token (bool | Unset):
        ou_code (str | Unset):
        tariff_id (str | Unset):
        ad_hoc_tariff_id (str | Unset):
        sim_card_number (str | Unset):
        is_new (bool | Unset):
        max_capacity_in_kw (float | Unset):
        product_id (str | Unset):
    """

    display_name: str | Unset = UNSET
    roaming_name: str | Unset = UNSET
    allow_any_token: bool | Unset = UNSET
    ou_code: str | Unset = UNSET
    tariff_id: str | Unset = UNSET
    ad_hoc_tariff_id: str | Unset = UNSET
    sim_card_number: str | Unset = UNSET
    is_new: bool | Unset = UNSET
    max_capacity_in_kw: float | Unset = UNSET
    product_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        display_name = self.display_name

        roaming_name = self.roaming_name

        allow_any_token = self.allow_any_token

        ou_code = self.ou_code

        tariff_id = self.tariff_id

        ad_hoc_tariff_id = self.ad_hoc_tariff_id

        sim_card_number = self.sim_card_number

        is_new = self.is_new

        max_capacity_in_kw = self.max_capacity_in_kw

        product_id = self.product_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if display_name is not UNSET:
            field_dict["displayName"] = display_name
        if roaming_name is not UNSET:
            field_dict["roamingName"] = roaming_name
        if allow_any_token is not UNSET:
            field_dict["allowAnyToken"] = allow_any_token
        if ou_code is not UNSET:
            field_dict["ouCode"] = ou_code
        if tariff_id is not UNSET:
            field_dict["tariffId"] = tariff_id
        if ad_hoc_tariff_id is not UNSET:
            field_dict["adHocTariffId"] = ad_hoc_tariff_id
        if sim_card_number is not UNSET:
            field_dict["simCardNumber"] = sim_card_number
        if is_new is not UNSET:
            field_dict["isNew"] = is_new
        if max_capacity_in_kw is not UNSET:
            field_dict["maxCapacityInKw"] = max_capacity_in_kw
        if product_id is not UNSET:
            field_dict["productId"] = product_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        display_name = d.pop("displayName", UNSET)

        roaming_name = d.pop("roamingName", UNSET)

        allow_any_token = d.pop("allowAnyToken", UNSET)

        ou_code = d.pop("ouCode", UNSET)

        tariff_id = d.pop("tariffId", UNSET)

        ad_hoc_tariff_id = d.pop("adHocTariffId", UNSET)

        sim_card_number = d.pop("simCardNumber", UNSET)

        is_new = d.pop("isNew", UNSET)

        max_capacity_in_kw = d.pop("maxCapacityInKw", UNSET)

        product_id = d.pop("productId", UNSET)

        chargepoint_put_dto = cls(
            display_name=display_name,
            roaming_name=roaming_name,
            allow_any_token=allow_any_token,
            ou_code=ou_code,
            tariff_id=tariff_id,
            ad_hoc_tariff_id=ad_hoc_tariff_id,
            sim_card_number=sim_card_number,
            is_new=is_new,
            max_capacity_in_kw=max_capacity_in_kw,
            product_id=product_id,
        )

        chargepoint_put_dto.additional_properties = d
        return chargepoint_put_dto

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

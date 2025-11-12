from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.private_emp_tariff_dto_power_type import PrivateEmpTariffDtoPowerType
from ..types import UNSET, Unset

T = TypeVar("T", bound="PrivateEmpTariffDto")


@_attrs_define
class PrivateEmpTariffDto:
    """
    Attributes:
        country_code (str | Unset):
        party_id (str | Unset):
        power_type (PrivateEmpTariffDtoPowerType | Unset):  Default: PrivateEmpTariffDtoPowerType.AC.
        min_power_in_wh (int | Unset):
        max_power_in_wh (int | Unset):
        use_public_tariff_when_kwh_is_cheaper (bool | Unset):
    """

    country_code: str | Unset = UNSET
    party_id: str | Unset = UNSET
    power_type: PrivateEmpTariffDtoPowerType | Unset = PrivateEmpTariffDtoPowerType.AC
    min_power_in_wh: int | Unset = UNSET
    max_power_in_wh: int | Unset = UNSET
    use_public_tariff_when_kwh_is_cheaper: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        country_code = self.country_code

        party_id = self.party_id

        power_type: str | Unset = UNSET
        if not isinstance(self.power_type, Unset):
            power_type = self.power_type.value

        min_power_in_wh = self.min_power_in_wh

        max_power_in_wh = self.max_power_in_wh

        use_public_tariff_when_kwh_is_cheaper = self.use_public_tariff_when_kwh_is_cheaper

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if country_code is not UNSET:
            field_dict["country_code"] = country_code
        if party_id is not UNSET:
            field_dict["party_id"] = party_id
        if power_type is not UNSET:
            field_dict["powerType"] = power_type
        if min_power_in_wh is not UNSET:
            field_dict["minPowerInWh"] = min_power_in_wh
        if max_power_in_wh is not UNSET:
            field_dict["maxPowerInWh"] = max_power_in_wh
        if use_public_tariff_when_kwh_is_cheaper is not UNSET:
            field_dict["usePublicTariffWhenKwhIsCheaper"] = use_public_tariff_when_kwh_is_cheaper

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        country_code = d.pop("country_code", UNSET)

        party_id = d.pop("party_id", UNSET)

        _power_type = d.pop("powerType", UNSET)
        power_type: PrivateEmpTariffDtoPowerType | Unset
        if isinstance(_power_type, Unset) or _power_type is None:
            power_type = UNSET
        else:
            power_type = PrivateEmpTariffDtoPowerType(_power_type)

        min_power_in_wh = d.pop("minPowerInWh", UNSET)

        max_power_in_wh = d.pop("maxPowerInWh", UNSET)

        use_public_tariff_when_kwh_is_cheaper = d.pop("usePublicTariffWhenKwhIsCheaper", UNSET)

        private_emp_tariff_dto = cls(
            country_code=country_code,
            party_id=party_id,
            power_type=power_type,
            min_power_in_wh=min_power_in_wh,
            max_power_in_wh=max_power_in_wh,
            use_public_tariff_when_kwh_is_cheaper=use_public_tariff_when_kwh_is_cheaper,
        )

        private_emp_tariff_dto.additional_properties = d
        return private_emp_tariff_dto

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

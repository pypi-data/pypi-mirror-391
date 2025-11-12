from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ItemCharacteristicsDto")


@_attrs_define
class ItemCharacteristicsDto:
    """
    Attributes:
        unit (str | Unset):
        data_type (str | Unset):
        min_limit (str | Unset):
        max_limit (str | Unset):
        values_list (str | Unset):
        supports_monitoring (bool | Unset):
    """

    unit: str | Unset = UNSET
    data_type: str | Unset = UNSET
    min_limit: str | Unset = UNSET
    max_limit: str | Unset = UNSET
    values_list: str | Unset = UNSET
    supports_monitoring: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        unit = self.unit

        data_type = self.data_type

        min_limit = self.min_limit

        max_limit = self.max_limit

        values_list = self.values_list

        supports_monitoring = self.supports_monitoring

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if unit is not UNSET:
            field_dict["unit"] = unit
        if data_type is not UNSET:
            field_dict["dataType"] = data_type
        if min_limit is not UNSET:
            field_dict["minLimit"] = min_limit
        if max_limit is not UNSET:
            field_dict["maxLimit"] = max_limit
        if values_list is not UNSET:
            field_dict["valuesList"] = values_list
        if supports_monitoring is not UNSET:
            field_dict["supportsMonitoring"] = supports_monitoring

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        unit = d.pop("unit", UNSET)

        data_type = d.pop("dataType", UNSET)

        min_limit = d.pop("minLimit", UNSET)

        max_limit = d.pop("maxLimit", UNSET)

        values_list = d.pop("valuesList", UNSET)

        supports_monitoring = d.pop("supportsMonitoring", UNSET)

        item_characteristics_dto = cls(
            unit=unit,
            data_type=data_type,
            min_limit=min_limit,
            max_limit=max_limit,
            values_list=values_list,
            supports_monitoring=supports_monitoring,
        )

        item_characteristics_dto.additional_properties = d
        return item_characteristics_dto

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

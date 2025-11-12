from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RegularHoursDto")


@_attrs_define
class RegularHoursDto:
    """
    Attributes:
        weekday (int | Unset):
        period_begin (str | Unset):
        period_end (str | Unset):
    """

    weekday: int | Unset = UNSET
    period_begin: str | Unset = UNSET
    period_end: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        weekday = self.weekday

        period_begin = self.period_begin

        period_end = self.period_end

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if weekday is not UNSET:
            field_dict["weekday"] = weekday
        if period_begin is not UNSET:
            field_dict["period_begin"] = period_begin
        if period_end is not UNSET:
            field_dict["period_end"] = period_end

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        weekday = d.pop("weekday", UNSET)

        period_begin = d.pop("period_begin", UNSET)

        period_end = d.pop("period_end", UNSET)

        regular_hours_dto = cls(
            weekday=weekday,
            period_begin=period_begin,
            period_end=period_end,
        )

        regular_hours_dto.additional_properties = d
        return regular_hours_dto

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

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChargingSchedulePeriod")


@_attrs_define
class ChargingSchedulePeriod:
    """
    Attributes:
        start_period (int):
        limit (float):
        number_phases (int | Unset):
    """

    start_period: int
    limit: float
    number_phases: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        start_period = self.start_period

        limit = self.limit

        number_phases = self.number_phases

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "startPeriod": start_period,
                "limit": limit,
            }
        )
        if number_phases is not UNSET:
            field_dict["numberPhases"] = number_phases

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        start_period = d.pop("startPeriod")

        limit = d.pop("limit")

        number_phases = d.pop("numberPhases", UNSET)

        charging_schedule_period = cls(
            start_period=start_period,
            limit=limit,
            number_phases=number_phases,
        )

        charging_schedule_period.additional_properties = d
        return charging_schedule_period

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

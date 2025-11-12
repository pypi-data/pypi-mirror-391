from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.charging_schedule_charging_rate_unit import ChargingScheduleChargingRateUnit
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.charging_schedule_period import ChargingSchedulePeriod


T = TypeVar("T", bound="ChargingSchedule")


@_attrs_define
class ChargingSchedule:
    """
    Attributes:
        charging_rate_unit (ChargingScheduleChargingRateUnit):  Default: ChargingScheduleChargingRateUnit.A.
        charging_schedule_period (list[ChargingSchedulePeriod]):
        duration (int | Unset):
        start_schedule (datetime.datetime | Unset):
        min_charging_rate (float | Unset):
    """

    charging_schedule_period: list[ChargingSchedulePeriod]
    charging_rate_unit: ChargingScheduleChargingRateUnit = ChargingScheduleChargingRateUnit.A
    duration: int | Unset = UNSET
    start_schedule: datetime.datetime | Unset = UNSET
    min_charging_rate: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        charging_rate_unit = self.charging_rate_unit.value

        charging_schedule_period = []
        for charging_schedule_period_item_data in self.charging_schedule_period:
            charging_schedule_period_item = charging_schedule_period_item_data.to_dict()
            charging_schedule_period.append(charging_schedule_period_item)

        duration = self.duration

        start_schedule: str | Unset = UNSET
        if not isinstance(self.start_schedule, Unset):
            start_schedule = self.start_schedule.isoformat()

        min_charging_rate = self.min_charging_rate

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "chargingRateUnit": charging_rate_unit,
                "chargingSchedulePeriod": charging_schedule_period,
            }
        )
        if duration is not UNSET:
            field_dict["duration"] = duration
        if start_schedule is not UNSET:
            field_dict["startSchedule"] = start_schedule
        if min_charging_rate is not UNSET:
            field_dict["minChargingRate"] = min_charging_rate

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.charging_schedule_period import ChargingSchedulePeriod

        d = dict(src_dict)
        charging_rate_unit = ChargingScheduleChargingRateUnit(d.pop("chargingRateUnit"))

        charging_schedule_period = []
        _charging_schedule_period = d.pop("chargingSchedulePeriod")
        for charging_schedule_period_item_data in _charging_schedule_period:
            charging_schedule_period_item = ChargingSchedulePeriod.from_dict(charging_schedule_period_item_data)

            charging_schedule_period.append(charging_schedule_period_item)

        duration = d.pop("duration", UNSET)

        _start_schedule = d.pop("startSchedule", UNSET)
        start_schedule: datetime.datetime | Unset
        if isinstance(_start_schedule, Unset) or _start_schedule is None:
            start_schedule = UNSET
        else:
            start_schedule = isoparse(_start_schedule)

        min_charging_rate = d.pop("minChargingRate", UNSET)

        charging_schedule = cls(
            charging_rate_unit=charging_rate_unit,
            charging_schedule_period=charging_schedule_period,
            duration=duration,
            start_schedule=start_schedule,
            min_charging_rate=min_charging_rate,
        )

        charging_schedule.additional_properties = d
        return charging_schedule

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

from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.tariff_restriction_day_of_week import TariffRestrictionDayOfWeek
from ..types import UNSET, Unset

T = TypeVar("T", bound="TariffRestriction")


@_attrs_define
class TariffRestriction:
    """
    Attributes:
        start_time (str | Unset):
        end_time (str | Unset):
        start_date (datetime.datetime | Unset):
        end_date (datetime.datetime | Unset):
        day_of_week (TariffRestrictionDayOfWeek | Unset):  Default: TariffRestrictionDayOfWeek.VALUE_0.
    """

    start_time: str | Unset = UNSET
    end_time: str | Unset = UNSET
    start_date: datetime.datetime | Unset = UNSET
    end_date: datetime.datetime | Unset = UNSET
    day_of_week: TariffRestrictionDayOfWeek | Unset = TariffRestrictionDayOfWeek.VALUE_0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        start_time = self.start_time

        end_time = self.end_time

        start_date: str | Unset = UNSET
        if not isinstance(self.start_date, Unset):
            start_date = self.start_date.isoformat()

        end_date: str | Unset = UNSET
        if not isinstance(self.end_date, Unset):
            end_date = self.end_date.isoformat()

        day_of_week: int | Unset = UNSET
        if not isinstance(self.day_of_week, Unset):
            day_of_week = self.day_of_week.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if start_time is not UNSET:
            field_dict["startTime"] = start_time
        if end_time is not UNSET:
            field_dict["endTime"] = end_time
        if start_date is not UNSET:
            field_dict["startDate"] = start_date
        if end_date is not UNSET:
            field_dict["endDate"] = end_date
        if day_of_week is not UNSET:
            field_dict["dayOfWeek"] = day_of_week

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        start_time = d.pop("startTime", UNSET)

        end_time = d.pop("endTime", UNSET)

        _start_date = d.pop("startDate", UNSET)
        start_date: datetime.datetime | Unset
        if isinstance(_start_date, Unset) or _start_date is None:
            start_date = UNSET
        else:
            start_date = isoparse(_start_date)

        _end_date = d.pop("endDate", UNSET)
        end_date: datetime.datetime | Unset
        if isinstance(_end_date, Unset) or _end_date is None:
            end_date = UNSET
        else:
            end_date = isoparse(_end_date)

        _day_of_week = d.pop("dayOfWeek", UNSET)
        day_of_week: TariffRestrictionDayOfWeek | Unset
        if isinstance(_day_of_week, Unset) or _day_of_week is None:
            day_of_week = UNSET
        else:
            day_of_week = TariffRestrictionDayOfWeek(_day_of_week)

        tariff_restriction = cls(
            start_time=start_time,
            end_time=end_time,
            start_date=start_date,
            end_date=end_date,
            day_of_week=day_of_week,
        )

        tariff_restriction.additional_properties = d
        return tariff_restriction

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

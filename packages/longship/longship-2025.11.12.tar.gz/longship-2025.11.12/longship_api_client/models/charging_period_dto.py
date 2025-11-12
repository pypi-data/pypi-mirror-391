from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChargingPeriodDto")


@_attrs_define
class ChargingPeriodDto:
    """
    Attributes:
        timestamp (datetime.datetime | Unset):
        delta_kwh (float | Unset):
        absolute_kwh (float | Unset):
        price (float | Unset):
        parking_time_minutes (float | Unset):
    """

    timestamp: datetime.datetime | Unset = UNSET
    delta_kwh: float | Unset = UNSET
    absolute_kwh: float | Unset = UNSET
    price: float | Unset = UNSET
    parking_time_minutes: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        timestamp: str | Unset = UNSET
        if not isinstance(self.timestamp, Unset):
            timestamp = self.timestamp.isoformat()

        delta_kwh = self.delta_kwh

        absolute_kwh = self.absolute_kwh

        price = self.price

        parking_time_minutes = self.parking_time_minutes

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp
        if delta_kwh is not UNSET:
            field_dict["deltaKwh"] = delta_kwh
        if absolute_kwh is not UNSET:
            field_dict["absoluteKwh"] = absolute_kwh
        if price is not UNSET:
            field_dict["price"] = price
        if parking_time_minutes is not UNSET:
            field_dict["parkingTimeMinutes"] = parking_time_minutes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _timestamp = d.pop("timestamp", UNSET)
        timestamp: datetime.datetime | Unset
        if isinstance(_timestamp, Unset) or _timestamp is None:
            timestamp = UNSET
        else:
            timestamp = isoparse(_timestamp)

        delta_kwh = d.pop("deltaKwh", UNSET)

        absolute_kwh = d.pop("absoluteKwh", UNSET)

        price = d.pop("price", UNSET)

        parking_time_minutes = d.pop("parkingTimeMinutes", UNSET)

        charging_period_dto = cls(
            timestamp=timestamp,
            delta_kwh=delta_kwh,
            absolute_kwh=absolute_kwh,
            price=price,
            parking_time_minutes=parking_time_minutes,
        )

        charging_period_dto.additional_properties = d
        return charging_period_dto

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

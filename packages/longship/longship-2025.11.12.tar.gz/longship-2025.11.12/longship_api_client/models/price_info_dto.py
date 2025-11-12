from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PriceInfoDto")


@_attrs_define
class PriceInfoDto:
    """
    Attributes:
        start_price (float | Unset):
        energy_price (float | Unset):
        total_parking_time_in_minutes (float | Unset):
        total_parking_time_steps (int | Unset):
        parking_time_price (float | Unset):
        total_charging_time_in_minutes (float | Unset):
        total_charging_time_steps (int | Unset):
        charging_time_price (float | Unset):
        total_price (float | Unset):
    """

    start_price: float | Unset = UNSET
    energy_price: float | Unset = UNSET
    total_parking_time_in_minutes: float | Unset = UNSET
    total_parking_time_steps: int | Unset = UNSET
    parking_time_price: float | Unset = UNSET
    total_charging_time_in_minutes: float | Unset = UNSET
    total_charging_time_steps: int | Unset = UNSET
    charging_time_price: float | Unset = UNSET
    total_price: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        start_price = self.start_price

        energy_price = self.energy_price

        total_parking_time_in_minutes = self.total_parking_time_in_minutes

        total_parking_time_steps = self.total_parking_time_steps

        parking_time_price = self.parking_time_price

        total_charging_time_in_minutes = self.total_charging_time_in_minutes

        total_charging_time_steps = self.total_charging_time_steps

        charging_time_price = self.charging_time_price

        total_price = self.total_price

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if start_price is not UNSET:
            field_dict["startPrice"] = start_price
        if energy_price is not UNSET:
            field_dict["energyPrice"] = energy_price
        if total_parking_time_in_minutes is not UNSET:
            field_dict["totalParkingTimeInMinutes"] = total_parking_time_in_minutes
        if total_parking_time_steps is not UNSET:
            field_dict["totalParkingTimeSteps"] = total_parking_time_steps
        if parking_time_price is not UNSET:
            field_dict["parkingTimePrice"] = parking_time_price
        if total_charging_time_in_minutes is not UNSET:
            field_dict["totalChargingTimeInMinutes"] = total_charging_time_in_minutes
        if total_charging_time_steps is not UNSET:
            field_dict["totalChargingTimeSteps"] = total_charging_time_steps
        if charging_time_price is not UNSET:
            field_dict["chargingTimePrice"] = charging_time_price
        if total_price is not UNSET:
            field_dict["totalPrice"] = total_price

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        start_price = d.pop("startPrice", UNSET)

        energy_price = d.pop("energyPrice", UNSET)

        total_parking_time_in_minutes = d.pop("totalParkingTimeInMinutes", UNSET)

        total_parking_time_steps = d.pop("totalParkingTimeSteps", UNSET)

        parking_time_price = d.pop("parkingTimePrice", UNSET)

        total_charging_time_in_minutes = d.pop("totalChargingTimeInMinutes", UNSET)

        total_charging_time_steps = d.pop("totalChargingTimeSteps", UNSET)

        charging_time_price = d.pop("chargingTimePrice", UNSET)

        total_price = d.pop("totalPrice", UNSET)

        price_info_dto = cls(
            start_price=start_price,
            energy_price=energy_price,
            total_parking_time_in_minutes=total_parking_time_in_minutes,
            total_parking_time_steps=total_parking_time_steps,
            parking_time_price=parking_time_price,
            total_charging_time_in_minutes=total_charging_time_in_minutes,
            total_charging_time_steps=total_charging_time_steps,
            charging_time_price=charging_time_price,
            total_price=total_price,
        )

        price_info_dto.additional_properties = d
        return price_info_dto

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

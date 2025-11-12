from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.charging_meter_value_dto_measurand import ChargingMeterValueDtoMeasurand
from ..models.charging_meter_value_dto_unit import ChargingMeterValueDtoUnit
from ..types import UNSET, Unset

T = TypeVar("T", bound="ChargingMeterValueDto")


@_attrs_define
class ChargingMeterValueDto:
    """
    Attributes:
        timestamp (datetime.datetime | Unset):
        value (str | Unset):
        measurand (ChargingMeterValueDtoMeasurand | Unset):  Default:
            ChargingMeterValueDtoMeasurand.ENERGY_ACTIVE_EXPORT_REGISTER.
        unit (ChargingMeterValueDtoUnit | Unset):  Default: ChargingMeterValueDtoUnit.WH.
    """

    timestamp: datetime.datetime | Unset = UNSET
    value: str | Unset = UNSET
    measurand: ChargingMeterValueDtoMeasurand | Unset = ChargingMeterValueDtoMeasurand.ENERGY_ACTIVE_EXPORT_REGISTER
    unit: ChargingMeterValueDtoUnit | Unset = ChargingMeterValueDtoUnit.WH
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        timestamp: str | Unset = UNSET
        if not isinstance(self.timestamp, Unset):
            timestamp = self.timestamp.isoformat()

        value = self.value

        measurand: str | Unset = UNSET
        if not isinstance(self.measurand, Unset):
            measurand = self.measurand.value

        unit: str | Unset = UNSET
        if not isinstance(self.unit, Unset):
            unit = self.unit.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp
        if value is not UNSET:
            field_dict["value"] = value
        if measurand is not UNSET:
            field_dict["measurand"] = measurand
        if unit is not UNSET:
            field_dict["unit"] = unit

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

        value = d.pop("value", UNSET)

        _measurand = d.pop("measurand", UNSET)
        measurand: ChargingMeterValueDtoMeasurand | Unset
        if isinstance(_measurand, Unset) or _measurand is None:
            measurand = UNSET
        else:
            measurand = ChargingMeterValueDtoMeasurand(_measurand)

        _unit = d.pop("unit", UNSET)
        unit: ChargingMeterValueDtoUnit | Unset
        if isinstance(_unit, Unset) or _unit is None:
            unit = UNSET
        else:
            unit = ChargingMeterValueDtoUnit(_unit)

        charging_meter_value_dto = cls(
            timestamp=timestamp,
            value=value,
            measurand=measurand,
            unit=unit,
        )

        charging_meter_value_dto.additional_properties = d
        return charging_meter_value_dto

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

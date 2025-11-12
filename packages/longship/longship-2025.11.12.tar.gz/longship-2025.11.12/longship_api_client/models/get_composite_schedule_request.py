from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.get_composite_schedule_request_charging_rate_unit import GetCompositeScheduleRequestChargingRateUnit
from ..types import UNSET, Unset

T = TypeVar("T", bound="GetCompositeScheduleRequest")


@_attrs_define
class GetCompositeScheduleRequest:
    """
    Attributes:
        connector_id (int):
        duration (int):
        charging_rate_unit (GetCompositeScheduleRequestChargingRateUnit | Unset):  Default:
            GetCompositeScheduleRequestChargingRateUnit.A.
    """

    connector_id: int
    duration: int
    charging_rate_unit: GetCompositeScheduleRequestChargingRateUnit | Unset = (
        GetCompositeScheduleRequestChargingRateUnit.A
    )
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        connector_id = self.connector_id

        duration = self.duration

        charging_rate_unit: str | Unset = UNSET
        if not isinstance(self.charging_rate_unit, Unset):
            charging_rate_unit = self.charging_rate_unit.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "connectorId": connector_id,
                "duration": duration,
            }
        )
        if charging_rate_unit is not UNSET:
            field_dict["chargingRateUnit"] = charging_rate_unit

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        connector_id = d.pop("connectorId")

        duration = d.pop("duration")

        _charging_rate_unit = d.pop("chargingRateUnit", UNSET)
        charging_rate_unit: GetCompositeScheduleRequestChargingRateUnit | Unset
        if isinstance(_charging_rate_unit, Unset) or _charging_rate_unit is None:
            charging_rate_unit = UNSET
        else:
            charging_rate_unit = GetCompositeScheduleRequestChargingRateUnit(_charging_rate_unit)

        get_composite_schedule_request = cls(
            connector_id=connector_id,
            duration=duration,
            charging_rate_unit=charging_rate_unit,
        )

        get_composite_schedule_request.additional_properties = d
        return get_composite_schedule_request

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

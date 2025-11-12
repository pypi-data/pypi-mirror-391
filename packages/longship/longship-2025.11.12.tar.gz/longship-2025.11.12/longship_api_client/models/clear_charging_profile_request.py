from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.clear_charging_profile_request_charging_profile_purpose import (
    ClearChargingProfileRequestChargingProfilePurpose,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="ClearChargingProfileRequest")


@_attrs_define
class ClearChargingProfileRequest:
    """
    Attributes:
        id (int | Unset):
        connector_id (int | Unset):
        charging_profile_purpose (ClearChargingProfileRequestChargingProfilePurpose | Unset):  Default:
            ClearChargingProfileRequestChargingProfilePurpose.CHARGEPOINTMAXPROFILE.
        stack_level (int | Unset):
    """

    id: int | Unset = UNSET
    connector_id: int | Unset = UNSET
    charging_profile_purpose: ClearChargingProfileRequestChargingProfilePurpose | Unset = (
        ClearChargingProfileRequestChargingProfilePurpose.CHARGEPOINTMAXPROFILE
    )
    stack_level: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        connector_id = self.connector_id

        charging_profile_purpose: str | Unset = UNSET
        if not isinstance(self.charging_profile_purpose, Unset):
            charging_profile_purpose = self.charging_profile_purpose.value

        stack_level = self.stack_level

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if connector_id is not UNSET:
            field_dict["connectorId"] = connector_id
        if charging_profile_purpose is not UNSET:
            field_dict["chargingProfilePurpose"] = charging_profile_purpose
        if stack_level is not UNSET:
            field_dict["stackLevel"] = stack_level

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        connector_id = d.pop("connectorId", UNSET)

        _charging_profile_purpose = d.pop("chargingProfilePurpose", UNSET)
        charging_profile_purpose: ClearChargingProfileRequestChargingProfilePurpose | Unset
        if isinstance(_charging_profile_purpose, Unset) or _charging_profile_purpose is None:
            charging_profile_purpose = UNSET
        else:
            charging_profile_purpose = ClearChargingProfileRequestChargingProfilePurpose(_charging_profile_purpose)

        stack_level = d.pop("stackLevel", UNSET)

        clear_charging_profile_request = cls(
            id=id,
            connector_id=connector_id,
            charging_profile_purpose=charging_profile_purpose,
            stack_level=stack_level,
        )

        clear_charging_profile_request.additional_properties = d
        return clear_charging_profile_request

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

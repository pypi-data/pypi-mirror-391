from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.cs_charging_profiles_charging_profile_kind import CsChargingProfilesChargingProfileKind
from ..models.cs_charging_profiles_charging_profile_purpose import CsChargingProfilesChargingProfilePurpose
from ..models.cs_charging_profiles_recurrency_kind import CsChargingProfilesRecurrencyKind
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.charging_schedule import ChargingSchedule


T = TypeVar("T", bound="CsChargingProfiles")


@_attrs_define
class CsChargingProfiles:
    """
    Attributes:
        charging_profile_id (int):
        stack_level (int):
        charging_profile_purpose (CsChargingProfilesChargingProfilePurpose):  Default:
            CsChargingProfilesChargingProfilePurpose.CHARGEPOINTMAXPROFILE.
        charging_profile_kind (CsChargingProfilesChargingProfileKind):  Default:
            CsChargingProfilesChargingProfileKind.ABSOLUTE.
        charging_schedule (ChargingSchedule):
        transaction_id (int | Unset):
        recurrency_kind (CsChargingProfilesRecurrencyKind | Unset):  Default: CsChargingProfilesRecurrencyKind.DAILY.
        valid_from (datetime.datetime | Unset):
        valid_to (datetime.datetime | Unset):
    """

    charging_profile_id: int
    stack_level: int
    charging_schedule: ChargingSchedule
    charging_profile_purpose: CsChargingProfilesChargingProfilePurpose = (
        CsChargingProfilesChargingProfilePurpose.CHARGEPOINTMAXPROFILE
    )
    charging_profile_kind: CsChargingProfilesChargingProfileKind = CsChargingProfilesChargingProfileKind.ABSOLUTE
    transaction_id: int | Unset = UNSET
    recurrency_kind: CsChargingProfilesRecurrencyKind | Unset = CsChargingProfilesRecurrencyKind.DAILY
    valid_from: datetime.datetime | Unset = UNSET
    valid_to: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        charging_profile_id = self.charging_profile_id

        stack_level = self.stack_level

        charging_profile_purpose = self.charging_profile_purpose.value

        charging_profile_kind = self.charging_profile_kind.value

        charging_schedule = self.charging_schedule.to_dict()

        transaction_id = self.transaction_id

        recurrency_kind: str | Unset = UNSET
        if not isinstance(self.recurrency_kind, Unset):
            recurrency_kind = self.recurrency_kind.value

        valid_from: str | Unset = UNSET
        if not isinstance(self.valid_from, Unset):
            valid_from = self.valid_from.isoformat()

        valid_to: str | Unset = UNSET
        if not isinstance(self.valid_to, Unset):
            valid_to = self.valid_to.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "chargingProfileId": charging_profile_id,
                "stackLevel": stack_level,
                "chargingProfilePurpose": charging_profile_purpose,
                "chargingProfileKind": charging_profile_kind,
                "chargingSchedule": charging_schedule,
            }
        )
        if transaction_id is not UNSET:
            field_dict["transactionId"] = transaction_id
        if recurrency_kind is not UNSET:
            field_dict["recurrencyKind"] = recurrency_kind
        if valid_from is not UNSET:
            field_dict["validFrom"] = valid_from
        if valid_to is not UNSET:
            field_dict["validTo"] = valid_to

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.charging_schedule import ChargingSchedule

        d = dict(src_dict)
        charging_profile_id = d.pop("chargingProfileId")

        stack_level = d.pop("stackLevel")

        charging_profile_purpose = CsChargingProfilesChargingProfilePurpose(d.pop("chargingProfilePurpose"))

        charging_profile_kind = CsChargingProfilesChargingProfileKind(d.pop("chargingProfileKind"))

        charging_schedule = ChargingSchedule.from_dict(d.pop("chargingSchedule"))

        transaction_id = d.pop("transactionId", UNSET)

        _recurrency_kind = d.pop("recurrencyKind", UNSET)
        recurrency_kind: CsChargingProfilesRecurrencyKind | Unset
        if isinstance(_recurrency_kind, Unset) or _recurrency_kind is None:
            recurrency_kind = UNSET
        else:
            recurrency_kind = CsChargingProfilesRecurrencyKind(_recurrency_kind)

        _valid_from = d.pop("validFrom", UNSET)
        valid_from: datetime.datetime | Unset
        if isinstance(_valid_from, Unset) or _valid_from is None:
            valid_from = UNSET
        else:
            valid_from = isoparse(_valid_from)

        _valid_to = d.pop("validTo", UNSET)
        valid_to: datetime.datetime | Unset
        if isinstance(_valid_to, Unset) or _valid_to is None:
            valid_to = UNSET
        else:
            valid_to = isoparse(_valid_to)

        cs_charging_profiles = cls(
            charging_profile_id=charging_profile_id,
            stack_level=stack_level,
            charging_profile_purpose=charging_profile_purpose,
            charging_profile_kind=charging_profile_kind,
            charging_schedule=charging_schedule,
            transaction_id=transaction_id,
            recurrency_kind=recurrency_kind,
            valid_from=valid_from,
            valid_to=valid_to,
        )

        cs_charging_profiles.additional_properties = d
        return cs_charging_profiles

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

from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.tariff_price_dto_approval_status import TariffPriceDtoApprovalStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.tariff_restriction import TariffRestriction


T = TypeVar("T", bound="TariffPriceDto")


@_attrs_define
class TariffPriceDto:
    """
    Attributes:
        created_timestamp (datetime.datetime | Unset):
        valid_from (datetime.datetime | Unset):
        start_tariff (float | Unset):
        price_per_kwh (float | Unset):
        price_per_kwh_incl_vat (float | Unset):
        is_vat_relevant (bool | Unset):
        parking_tariff (float | Unset):
        parking_step_size_in_minutes (int | Unset):
        parking_grace_period_in_minutes (int | Unset):
        parking_tariff_restrictions (list[TariffRestriction] | Unset):
        parking_always_active_after_in_minutes (int | Unset):
        time_tariff (float | Unset):
        time_step_size_in_minutes (int | Unset):
        time_grace_period_in_minutes (int | Unset):
        approval_status (TariffPriceDtoApprovalStatus | Unset):  Default: TariffPriceDtoApprovalStatus.PENDING.
    """

    created_timestamp: datetime.datetime | Unset = UNSET
    valid_from: datetime.datetime | Unset = UNSET
    start_tariff: float | Unset = UNSET
    price_per_kwh: float | Unset = UNSET
    price_per_kwh_incl_vat: float | Unset = UNSET
    is_vat_relevant: bool | Unset = UNSET
    parking_tariff: float | Unset = UNSET
    parking_step_size_in_minutes: int | Unset = UNSET
    parking_grace_period_in_minutes: int | Unset = UNSET
    parking_tariff_restrictions: list[TariffRestriction] | Unset = UNSET
    parking_always_active_after_in_minutes: int | Unset = UNSET
    time_tariff: float | Unset = UNSET
    time_step_size_in_minutes: int | Unset = UNSET
    time_grace_period_in_minutes: int | Unset = UNSET
    approval_status: TariffPriceDtoApprovalStatus | Unset = TariffPriceDtoApprovalStatus.PENDING
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_timestamp: str | Unset = UNSET
        if not isinstance(self.created_timestamp, Unset):
            created_timestamp = self.created_timestamp.isoformat()

        valid_from: str | Unset = UNSET
        if not isinstance(self.valid_from, Unset):
            valid_from = self.valid_from.isoformat()

        start_tariff = self.start_tariff

        price_per_kwh = self.price_per_kwh

        price_per_kwh_incl_vat = self.price_per_kwh_incl_vat

        is_vat_relevant = self.is_vat_relevant

        parking_tariff = self.parking_tariff

        parking_step_size_in_minutes = self.parking_step_size_in_minutes

        parking_grace_period_in_minutes = self.parking_grace_period_in_minutes

        parking_tariff_restrictions: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.parking_tariff_restrictions, Unset):
            parking_tariff_restrictions = []
            for parking_tariff_restrictions_item_data in self.parking_tariff_restrictions:
                parking_tariff_restrictions_item = parking_tariff_restrictions_item_data.to_dict()
                parking_tariff_restrictions.append(parking_tariff_restrictions_item)

        parking_always_active_after_in_minutes = self.parking_always_active_after_in_minutes

        time_tariff = self.time_tariff

        time_step_size_in_minutes = self.time_step_size_in_minutes

        time_grace_period_in_minutes = self.time_grace_period_in_minutes

        approval_status: str | Unset = UNSET
        if not isinstance(self.approval_status, Unset):
            approval_status = self.approval_status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if created_timestamp is not UNSET:
            field_dict["createdTimestamp"] = created_timestamp
        if valid_from is not UNSET:
            field_dict["validFrom"] = valid_from
        if start_tariff is not UNSET:
            field_dict["startTariff"] = start_tariff
        if price_per_kwh is not UNSET:
            field_dict["pricePerKwh"] = price_per_kwh
        if price_per_kwh_incl_vat is not UNSET:
            field_dict["pricePerKwhInclVat"] = price_per_kwh_incl_vat
        if is_vat_relevant is not UNSET:
            field_dict["isVatRelevant"] = is_vat_relevant
        if parking_tariff is not UNSET:
            field_dict["parkingTariff"] = parking_tariff
        if parking_step_size_in_minutes is not UNSET:
            field_dict["parkingStepSizeInMinutes"] = parking_step_size_in_minutes
        if parking_grace_period_in_minutes is not UNSET:
            field_dict["parkingGracePeriodInMinutes"] = parking_grace_period_in_minutes
        if parking_tariff_restrictions is not UNSET:
            field_dict["parkingTariffRestrictions"] = parking_tariff_restrictions
        if parking_always_active_after_in_minutes is not UNSET:
            field_dict["parkingAlwaysActiveAfterInMinutes"] = parking_always_active_after_in_minutes
        if time_tariff is not UNSET:
            field_dict["timeTariff"] = time_tariff
        if time_step_size_in_minutes is not UNSET:
            field_dict["timeStepSizeInMinutes"] = time_step_size_in_minutes
        if time_grace_period_in_minutes is not UNSET:
            field_dict["timeGracePeriodInMinutes"] = time_grace_period_in_minutes
        if approval_status is not UNSET:
            field_dict["approvalStatus"] = approval_status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tariff_restriction import TariffRestriction

        d = dict(src_dict)
        _created_timestamp = d.pop("createdTimestamp", UNSET)
        created_timestamp: datetime.datetime | Unset
        if isinstance(_created_timestamp, Unset) or _created_timestamp is None:
            created_timestamp = UNSET
        else:
            created_timestamp = isoparse(_created_timestamp)

        _valid_from = d.pop("validFrom", UNSET)
        valid_from: datetime.datetime | Unset
        if isinstance(_valid_from, Unset) or _valid_from is None:
            valid_from = UNSET
        else:
            valid_from = isoparse(_valid_from)

        start_tariff = d.pop("startTariff", UNSET)

        price_per_kwh = d.pop("pricePerKwh", UNSET)

        price_per_kwh_incl_vat = d.pop("pricePerKwhInclVat", UNSET)

        is_vat_relevant = d.pop("isVatRelevant", UNSET)

        parking_tariff = d.pop("parkingTariff", UNSET)

        parking_step_size_in_minutes = d.pop("parkingStepSizeInMinutes", UNSET)

        parking_grace_period_in_minutes = d.pop("parkingGracePeriodInMinutes", UNSET)

        parking_tariff_restrictions = []
        _parking_tariff_restrictions = d.pop("parkingTariffRestrictions", UNSET)
        for parking_tariff_restrictions_item_data in _parking_tariff_restrictions or []:
            parking_tariff_restrictions_item = TariffRestriction.from_dict(parking_tariff_restrictions_item_data)

            parking_tariff_restrictions.append(parking_tariff_restrictions_item)

        parking_always_active_after_in_minutes = d.pop("parkingAlwaysActiveAfterInMinutes", UNSET)

        time_tariff = d.pop("timeTariff", UNSET)

        time_step_size_in_minutes = d.pop("timeStepSizeInMinutes", UNSET)

        time_grace_period_in_minutes = d.pop("timeGracePeriodInMinutes", UNSET)

        _approval_status = d.pop("approvalStatus", UNSET)
        approval_status: TariffPriceDtoApprovalStatus | Unset
        if isinstance(_approval_status, Unset) or _approval_status is None:
            approval_status = UNSET
        else:
            approval_status = TariffPriceDtoApprovalStatus(_approval_status)

        tariff_price_dto = cls(
            created_timestamp=created_timestamp,
            valid_from=valid_from,
            start_tariff=start_tariff,
            price_per_kwh=price_per_kwh,
            price_per_kwh_incl_vat=price_per_kwh_incl_vat,
            is_vat_relevant=is_vat_relevant,
            parking_tariff=parking_tariff,
            parking_step_size_in_minutes=parking_step_size_in_minutes,
            parking_grace_period_in_minutes=parking_grace_period_in_minutes,
            parking_tariff_restrictions=parking_tariff_restrictions,
            parking_always_active_after_in_minutes=parking_always_active_after_in_minutes,
            time_tariff=time_tariff,
            time_step_size_in_minutes=time_step_size_in_minutes,
            time_grace_period_in_minutes=time_grace_period_in_minutes,
            approval_status=approval_status,
        )

        tariff_price_dto.additional_properties = d
        return tariff_price_dto

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

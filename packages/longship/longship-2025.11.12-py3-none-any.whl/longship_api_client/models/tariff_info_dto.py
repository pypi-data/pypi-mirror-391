from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.tariff_info_dto_tariff_type import TariffInfoDtoTariffType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.tariff_assertion_dto import TariffAssertionDto


T = TypeVar("T", bound="TariffInfoDto")


@_attrs_define
class TariffInfoDto:
    """
    Attributes:
        tariff_id (str | Unset):
        tariff_name (str | Unset):
        start_tariff (float | Unset):
        tariff_price (float | Unset):
        parking_tariff (float | Unset):
        parking_step_size_in_minutes (int | Unset):
        parking_grace_period_in_minutes (int | Unset):
        parking_always_active_after_in_minutes (int | Unset):
        time_tariff (float | Unset):
        time_step_size_in_minutes (int | Unset):
        time_grace_period_in_minutes (int | Unset):
        tariff_type (TariffInfoDtoTariffType | Unset):  Default: TariffInfoDtoTariffType.REIMBURSEMENTTARIFF.
        assertions (list[TariffAssertionDto] | Unset):
    """

    tariff_id: str | Unset = UNSET
    tariff_name: str | Unset = UNSET
    start_tariff: float | Unset = UNSET
    tariff_price: float | Unset = UNSET
    parking_tariff: float | Unset = UNSET
    parking_step_size_in_minutes: int | Unset = UNSET
    parking_grace_period_in_minutes: int | Unset = UNSET
    parking_always_active_after_in_minutes: int | Unset = UNSET
    time_tariff: float | Unset = UNSET
    time_step_size_in_minutes: int | Unset = UNSET
    time_grace_period_in_minutes: int | Unset = UNSET
    tariff_type: TariffInfoDtoTariffType | Unset = TariffInfoDtoTariffType.REIMBURSEMENTTARIFF
    assertions: list[TariffAssertionDto] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tariff_id = self.tariff_id

        tariff_name = self.tariff_name

        start_tariff = self.start_tariff

        tariff_price = self.tariff_price

        parking_tariff = self.parking_tariff

        parking_step_size_in_minutes = self.parking_step_size_in_minutes

        parking_grace_period_in_minutes = self.parking_grace_period_in_minutes

        parking_always_active_after_in_minutes = self.parking_always_active_after_in_minutes

        time_tariff = self.time_tariff

        time_step_size_in_minutes = self.time_step_size_in_minutes

        time_grace_period_in_minutes = self.time_grace_period_in_minutes

        tariff_type: str | Unset = UNSET
        if not isinstance(self.tariff_type, Unset):
            tariff_type = self.tariff_type.value

        assertions: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.assertions, Unset):
            assertions = []
            for assertions_item_data in self.assertions:
                assertions_item = assertions_item_data.to_dict()
                assertions.append(assertions_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if tariff_id is not UNSET:
            field_dict["tariffId"] = tariff_id
        if tariff_name is not UNSET:
            field_dict["tariffName"] = tariff_name
        if start_tariff is not UNSET:
            field_dict["startTariff"] = start_tariff
        if tariff_price is not UNSET:
            field_dict["tariffPrice"] = tariff_price
        if parking_tariff is not UNSET:
            field_dict["parkingTariff"] = parking_tariff
        if parking_step_size_in_minutes is not UNSET:
            field_dict["parkingStepSizeInMinutes"] = parking_step_size_in_minutes
        if parking_grace_period_in_minutes is not UNSET:
            field_dict["parkingGracePeriodInMinutes"] = parking_grace_period_in_minutes
        if parking_always_active_after_in_minutes is not UNSET:
            field_dict["parkingAlwaysActiveAfterInMinutes"] = parking_always_active_after_in_minutes
        if time_tariff is not UNSET:
            field_dict["timeTariff"] = time_tariff
        if time_step_size_in_minutes is not UNSET:
            field_dict["timeStepSizeInMinutes"] = time_step_size_in_minutes
        if time_grace_period_in_minutes is not UNSET:
            field_dict["timeGracePeriodInMinutes"] = time_grace_period_in_minutes
        if tariff_type is not UNSET:
            field_dict["tariffType"] = tariff_type
        if assertions is not UNSET:
            field_dict["assertions"] = assertions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tariff_assertion_dto import TariffAssertionDto

        d = dict(src_dict)
        tariff_id = d.pop("tariffId", UNSET)

        tariff_name = d.pop("tariffName", UNSET)

        start_tariff = d.pop("startTariff", UNSET)

        tariff_price = d.pop("tariffPrice", UNSET)

        parking_tariff = d.pop("parkingTariff", UNSET)

        parking_step_size_in_minutes = d.pop("parkingStepSizeInMinutes", UNSET)

        parking_grace_period_in_minutes = d.pop("parkingGracePeriodInMinutes", UNSET)

        parking_always_active_after_in_minutes = d.pop("parkingAlwaysActiveAfterInMinutes", UNSET)

        time_tariff = d.pop("timeTariff", UNSET)

        time_step_size_in_minutes = d.pop("timeStepSizeInMinutes", UNSET)

        time_grace_period_in_minutes = d.pop("timeGracePeriodInMinutes", UNSET)

        _tariff_type = d.pop("tariffType", UNSET)
        tariff_type: TariffInfoDtoTariffType | Unset
        if isinstance(_tariff_type, Unset):
            tariff_type = UNSET
        else:
            tariff_type = TariffInfoDtoTariffType(_tariff_type)

        assertions = []
        _assertions = d.pop("assertions", UNSET)
        for assertions_item_data in _assertions or []:
            assertions_item = TariffAssertionDto.from_dict(assertions_item_data)

            assertions.append(assertions_item)

        tariff_info_dto = cls(
            tariff_id=tariff_id,
            tariff_name=tariff_name,
            start_tariff=start_tariff,
            tariff_price=tariff_price,
            parking_tariff=parking_tariff,
            parking_step_size_in_minutes=parking_step_size_in_minutes,
            parking_grace_period_in_minutes=parking_grace_period_in_minutes,
            parking_always_active_after_in_minutes=parking_always_active_after_in_minutes,
            time_tariff=time_tariff,
            time_step_size_in_minutes=time_step_size_in_minutes,
            time_grace_period_in_minutes=time_grace_period_in_minutes,
            tariff_type=tariff_type,
            assertions=assertions,
        )

        tariff_info_dto.additional_properties = d
        return tariff_info_dto

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

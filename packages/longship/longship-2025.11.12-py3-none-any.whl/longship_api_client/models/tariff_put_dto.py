from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.tariff_put_dto_reimburse_type import TariffPutDtoReimburseType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pricing_element import PricingElement
    from ..models.private_emp_tariff_dto import PrivateEmpTariffDto
    from ..models.reimburse_token import ReimburseToken
    from ..models.tariff_restriction import TariffRestriction


T = TypeVar("T", bound="TariffPutDto")


@_attrs_define
class TariffPutDto:
    """
    Attributes:
        name (str | Unset):
        hubject_id (str | Unset):
        private_emp_tariff (PrivateEmpTariffDto | Unset):
        start_tariff (float | Unset):
        price (float | Unset):
        parking_tariff (float | Unset):
        parking_step_size_in_minutes (int | Unset):
        parking_grace_period_in_minutes (int | Unset):
        parking_tariff_restrictions (list[TariffRestriction] | Unset):
        parking_always_active_after_in_minutes (int | Unset):
        time_tariff (float | Unset):
        time_step_size_in_minutes (int | Unset):
        time_grace_period_in_minutes (int | Unset):
        external_reference (str | Unset):
        deleted (datetime.datetime | Unset):
        reimburse_type (TariffPutDtoReimburseType | Unset):  Default: TariffPutDtoReimburseType.ORGANIZATIONUNIT.
        reimburse_tokens (list[ReimburseToken] | Unset):
        location_id (str | Unset):
        ou (str | Unset):
        ou_id (str | Unset):
        ou_name (str | Unset):
        pricing_elements (list[PricingElement] | Unset):
    """

    name: str | Unset = UNSET
    hubject_id: str | Unset = UNSET
    private_emp_tariff: PrivateEmpTariffDto | Unset = UNSET
    start_tariff: float | Unset = UNSET
    price: float | Unset = UNSET
    parking_tariff: float | Unset = UNSET
    parking_step_size_in_minutes: int | Unset = UNSET
    parking_grace_period_in_minutes: int | Unset = UNSET
    parking_tariff_restrictions: list[TariffRestriction] | Unset = UNSET
    parking_always_active_after_in_minutes: int | Unset = UNSET
    time_tariff: float | Unset = UNSET
    time_step_size_in_minutes: int | Unset = UNSET
    time_grace_period_in_minutes: int | Unset = UNSET
    external_reference: str | Unset = UNSET
    deleted: datetime.datetime | Unset = UNSET
    reimburse_type: TariffPutDtoReimburseType | Unset = TariffPutDtoReimburseType.ORGANIZATIONUNIT
    reimburse_tokens: list[ReimburseToken] | Unset = UNSET
    location_id: str | Unset = UNSET
    ou: str | Unset = UNSET
    ou_id: str | Unset = UNSET
    ou_name: str | Unset = UNSET
    pricing_elements: list[PricingElement] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        hubject_id = self.hubject_id

        private_emp_tariff: dict[str, Any] | Unset = UNSET
        if not isinstance(self.private_emp_tariff, Unset):
            private_emp_tariff = self.private_emp_tariff.to_dict()

        start_tariff = self.start_tariff

        price = self.price

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

        external_reference = self.external_reference

        deleted: str | Unset = UNSET
        if not isinstance(self.deleted, Unset):
            deleted = self.deleted.isoformat()

        reimburse_type: str | Unset = UNSET
        if not isinstance(self.reimburse_type, Unset):
            reimburse_type = self.reimburse_type.value

        reimburse_tokens: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.reimburse_tokens, Unset):
            reimburse_tokens = []
            for reimburse_tokens_item_data in self.reimburse_tokens:
                reimburse_tokens_item = reimburse_tokens_item_data.to_dict()
                reimburse_tokens.append(reimburse_tokens_item)

        location_id = self.location_id

        ou = self.ou

        ou_id = self.ou_id

        ou_name = self.ou_name

        pricing_elements: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.pricing_elements, Unset):
            pricing_elements = []
            for pricing_elements_item_data in self.pricing_elements:
                pricing_elements_item = pricing_elements_item_data.to_dict()
                pricing_elements.append(pricing_elements_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if hubject_id is not UNSET:
            field_dict["hubjectId"] = hubject_id
        if private_emp_tariff is not UNSET:
            field_dict["privateEmpTariff"] = private_emp_tariff
        if start_tariff is not UNSET:
            field_dict["startTariff"] = start_tariff
        if price is not UNSET:
            field_dict["price"] = price
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
        if external_reference is not UNSET:
            field_dict["externalReference"] = external_reference
        if deleted is not UNSET:
            field_dict["deleted"] = deleted
        if reimburse_type is not UNSET:
            field_dict["reimburseType"] = reimburse_type
        if reimburse_tokens is not UNSET:
            field_dict["reimburseTokens"] = reimburse_tokens
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if ou is not UNSET:
            field_dict["ou"] = ou
        if ou_id is not UNSET:
            field_dict["ouId"] = ou_id
        if ou_name is not UNSET:
            field_dict["ouName"] = ou_name
        if pricing_elements is not UNSET:
            field_dict["pricingElements"] = pricing_elements

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.pricing_element import PricingElement
        from ..models.private_emp_tariff_dto import PrivateEmpTariffDto
        from ..models.reimburse_token import ReimburseToken
        from ..models.tariff_restriction import TariffRestriction

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        hubject_id = d.pop("hubjectId", UNSET)

        _private_emp_tariff = d.pop("privateEmpTariff", UNSET)
        private_emp_tariff: PrivateEmpTariffDto | Unset
        if isinstance(_private_emp_tariff, Unset) or _private_emp_tariff is None:
            private_emp_tariff = UNSET
        else:
            private_emp_tariff = PrivateEmpTariffDto.from_dict(_private_emp_tariff)

        start_tariff = d.pop("startTariff", UNSET)

        price = d.pop("price", UNSET)

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

        external_reference = d.pop("externalReference", UNSET)

        _deleted = d.pop("deleted", UNSET)
        deleted: datetime.datetime | Unset
        if isinstance(_deleted, Unset) or _deleted is None:
            deleted = UNSET
        else:
            deleted = isoparse(_deleted)

        _reimburse_type = d.pop("reimburseType", UNSET)
        reimburse_type: TariffPutDtoReimburseType | Unset
        if isinstance(_reimburse_type, Unset) or _reimburse_type is None:
            reimburse_type = UNSET
        else:
            reimburse_type = TariffPutDtoReimburseType(_reimburse_type)

        reimburse_tokens = []
        _reimburse_tokens = d.pop("reimburseTokens", UNSET)
        for reimburse_tokens_item_data in _reimburse_tokens or []:
            reimburse_tokens_item = ReimburseToken.from_dict(reimburse_tokens_item_data)

            reimburse_tokens.append(reimburse_tokens_item)

        location_id = d.pop("locationId", UNSET)

        ou = d.pop("ou", UNSET)

        ou_id = d.pop("ouId", UNSET)

        ou_name = d.pop("ouName", UNSET)

        pricing_elements = []
        _pricing_elements = d.pop("pricingElements", UNSET)
        for pricing_elements_item_data in _pricing_elements or []:
            pricing_elements_item = PricingElement.from_dict(pricing_elements_item_data)

            pricing_elements.append(pricing_elements_item)

        tariff_put_dto = cls(
            name=name,
            hubject_id=hubject_id,
            private_emp_tariff=private_emp_tariff,
            start_tariff=start_tariff,
            price=price,
            parking_tariff=parking_tariff,
            parking_step_size_in_minutes=parking_step_size_in_minutes,
            parking_grace_period_in_minutes=parking_grace_period_in_minutes,
            parking_tariff_restrictions=parking_tariff_restrictions,
            parking_always_active_after_in_minutes=parking_always_active_after_in_minutes,
            time_tariff=time_tariff,
            time_step_size_in_minutes=time_step_size_in_minutes,
            time_grace_period_in_minutes=time_grace_period_in_minutes,
            external_reference=external_reference,
            deleted=deleted,
            reimburse_type=reimburse_type,
            reimburse_tokens=reimburse_tokens,
            location_id=location_id,
            ou=ou,
            ou_id=ou_id,
            ou_name=ou_name,
            pricing_elements=pricing_elements,
        )

        tariff_put_dto.additional_properties = d
        return tariff_put_dto

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

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.tariff_post_dto_reimburse_type import TariffPostDtoReimburseType
from ..models.tariff_post_dto_tariff_type import TariffPostDtoTariffType
from ..models.tariff_post_dto_usage_type import TariffPostDtoUsageType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pricing_element import PricingElement
    from ..models.private_emp_tariff_dto import PrivateEmpTariffDto
    from ..models.reimburse_token import ReimburseToken
    from ..models.tariff_restriction import TariffRestriction


T = TypeVar("T", bound="TariffPostDto")


@_attrs_define
class TariffPostDto:
    """
    Attributes:
        name (str | Unset):
        currency (str | Unset):
        usage_type (TariffPostDtoUsageType | Unset):  Default: TariffPostDtoUsageType.SELL.
        tariff_type (TariffPostDtoTariffType | Unset):  Default: TariffPostDtoTariffType.REGULAR.
        private_emp_tariff (PrivateEmpTariffDto | Unset):
        start_tariff (float | Unset):
        price (float | Unset):
        parking_tariff (float | Unset):
        parking_step_size_in_minutes (int | Unset):
        parking_grace_period_in_minutes (int | Unset):
        parking_always_active_after_in_minutes (int | Unset):
        parking_tariff_restrictions (list[TariffRestriction] | Unset):
        time_tariff (float | Unset):
        time_step_size_in_minutes (int | Unset):
        time_grace_period_in_minutes (int | Unset):
        external_reference (str | Unset):
        ocpi_id (str | Unset):
        reimburse_type (TariffPostDtoReimburseType | Unset):  Default: TariffPostDtoReimburseType.ORGANIZATIONUNIT.
        reimburse_tokens (list[ReimburseToken] | Unset):
        location_id (str | Unset):
        ou (str | Unset):
        ou_id (str | Unset):
        ou_name (str | Unset):
        pricing_elements (list[PricingElement] | Unset):
    """

    name: str | Unset = UNSET
    currency: str | Unset = UNSET
    usage_type: TariffPostDtoUsageType | Unset = TariffPostDtoUsageType.SELL
    tariff_type: TariffPostDtoTariffType | Unset = TariffPostDtoTariffType.REGULAR
    private_emp_tariff: PrivateEmpTariffDto | Unset = UNSET
    start_tariff: float | Unset = UNSET
    price: float | Unset = UNSET
    parking_tariff: float | Unset = UNSET
    parking_step_size_in_minutes: int | Unset = UNSET
    parking_grace_period_in_minutes: int | Unset = UNSET
    parking_always_active_after_in_minutes: int | Unset = UNSET
    parking_tariff_restrictions: list[TariffRestriction] | Unset = UNSET
    time_tariff: float | Unset = UNSET
    time_step_size_in_minutes: int | Unset = UNSET
    time_grace_period_in_minutes: int | Unset = UNSET
    external_reference: str | Unset = UNSET
    ocpi_id: str | Unset = UNSET
    reimburse_type: TariffPostDtoReimburseType | Unset = TariffPostDtoReimburseType.ORGANIZATIONUNIT
    reimburse_tokens: list[ReimburseToken] | Unset = UNSET
    location_id: str | Unset = UNSET
    ou: str | Unset = UNSET
    ou_id: str | Unset = UNSET
    ou_name: str | Unset = UNSET
    pricing_elements: list[PricingElement] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        currency = self.currency

        usage_type: str | Unset = UNSET
        if not isinstance(self.usage_type, Unset):
            usage_type = self.usage_type.value

        tariff_type: str | Unset = UNSET
        if not isinstance(self.tariff_type, Unset):
            tariff_type = self.tariff_type.value

        private_emp_tariff: dict[str, Any] | Unset = UNSET
        if not isinstance(self.private_emp_tariff, Unset):
            private_emp_tariff = self.private_emp_tariff.to_dict()

        start_tariff = self.start_tariff

        price = self.price

        parking_tariff = self.parking_tariff

        parking_step_size_in_minutes = self.parking_step_size_in_minutes

        parking_grace_period_in_minutes = self.parking_grace_period_in_minutes

        parking_always_active_after_in_minutes = self.parking_always_active_after_in_minutes

        parking_tariff_restrictions: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.parking_tariff_restrictions, Unset):
            parking_tariff_restrictions = []
            for parking_tariff_restrictions_item_data in self.parking_tariff_restrictions:
                parking_tariff_restrictions_item = parking_tariff_restrictions_item_data.to_dict()
                parking_tariff_restrictions.append(parking_tariff_restrictions_item)

        time_tariff = self.time_tariff

        time_step_size_in_minutes = self.time_step_size_in_minutes

        time_grace_period_in_minutes = self.time_grace_period_in_minutes

        external_reference = self.external_reference

        ocpi_id = self.ocpi_id

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
        if currency is not UNSET:
            field_dict["currency"] = currency
        if usage_type is not UNSET:
            field_dict["usageType"] = usage_type
        if tariff_type is not UNSET:
            field_dict["tariffType"] = tariff_type
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
        if parking_always_active_after_in_minutes is not UNSET:
            field_dict["parkingAlwaysActiveAfterInMinutes"] = parking_always_active_after_in_minutes
        if parking_tariff_restrictions is not UNSET:
            field_dict["parkingTariffRestrictions"] = parking_tariff_restrictions
        if time_tariff is not UNSET:
            field_dict["timeTariff"] = time_tariff
        if time_step_size_in_minutes is not UNSET:
            field_dict["timeStepSizeInMinutes"] = time_step_size_in_minutes
        if time_grace_period_in_minutes is not UNSET:
            field_dict["timeGracePeriodInMinutes"] = time_grace_period_in_minutes
        if external_reference is not UNSET:
            field_dict["externalReference"] = external_reference
        if ocpi_id is not UNSET:
            field_dict["ocpiId"] = ocpi_id
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

        currency = d.pop("currency", UNSET)

        _usage_type = d.pop("usageType", UNSET)
        usage_type: TariffPostDtoUsageType | Unset
        if isinstance(_usage_type, Unset) or _usage_type is None:
            usage_type = UNSET
        else:
            usage_type = TariffPostDtoUsageType(_usage_type)

        _tariff_type = d.pop("tariffType", UNSET)
        tariff_type: TariffPostDtoTariffType | Unset
        if isinstance(_tariff_type, Unset) or _tariff_type is None:
            tariff_type = UNSET
        else:
            tariff_type = TariffPostDtoTariffType(_tariff_type)

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

        parking_always_active_after_in_minutes = d.pop("parkingAlwaysActiveAfterInMinutes", UNSET)

        parking_tariff_restrictions = []
        _parking_tariff_restrictions = d.pop("parkingTariffRestrictions", UNSET)
        for parking_tariff_restrictions_item_data in _parking_tariff_restrictions or []:
            parking_tariff_restrictions_item = TariffRestriction.from_dict(parking_tariff_restrictions_item_data)

            parking_tariff_restrictions.append(parking_tariff_restrictions_item)

        time_tariff = d.pop("timeTariff", UNSET)

        time_step_size_in_minutes = d.pop("timeStepSizeInMinutes", UNSET)

        time_grace_period_in_minutes = d.pop("timeGracePeriodInMinutes", UNSET)

        external_reference = d.pop("externalReference", UNSET)

        ocpi_id = d.pop("ocpiId", UNSET)

        _reimburse_type = d.pop("reimburseType", UNSET)
        reimburse_type: TariffPostDtoReimburseType | Unset
        if isinstance(_reimburse_type, Unset) or _reimburse_type is None:
            reimburse_type = UNSET
        else:
            reimburse_type = TariffPostDtoReimburseType(_reimburse_type)

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

        tariff_post_dto = cls(
            name=name,
            currency=currency,
            usage_type=usage_type,
            tariff_type=tariff_type,
            private_emp_tariff=private_emp_tariff,
            start_tariff=start_tariff,
            price=price,
            parking_tariff=parking_tariff,
            parking_step_size_in_minutes=parking_step_size_in_minutes,
            parking_grace_period_in_minutes=parking_grace_period_in_minutes,
            parking_always_active_after_in_minutes=parking_always_active_after_in_minutes,
            parking_tariff_restrictions=parking_tariff_restrictions,
            time_tariff=time_tariff,
            time_step_size_in_minutes=time_step_size_in_minutes,
            time_grace_period_in_minutes=time_grace_period_in_minutes,
            external_reference=external_reference,
            ocpi_id=ocpi_id,
            reimburse_type=reimburse_type,
            reimburse_tokens=reimburse_tokens,
            location_id=location_id,
            ou=ou,
            ou_id=ou_id,
            ou_name=ou_name,
            pricing_elements=pricing_elements,
        )

        tariff_post_dto.additional_properties = d
        return tariff_post_dto

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

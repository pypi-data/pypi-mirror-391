from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.tariff_dto_reimburse_type import TariffDtoReimburseType
from ..models.tariff_dto_tariff_type import TariffDtoTariffType
from ..models.tariff_dto_usage_type import TariffDtoUsageType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pricing_element import PricingElement
    from ..models.private_emp_tariff_dto import PrivateEmpTariffDto
    from ..models.reimburse_token import ReimburseToken
    from ..models.tariff_price_dto import TariffPriceDto
    from ..models.tariff_restriction import TariffRestriction


T = TypeVar("T", bound="TariffDto")


@_attrs_define
class TariffDto:
    """
    Attributes:
        tenant_id (str):
        id (str | Unset):
        ocpi_id (str | Unset):
        hubject_id (str | Unset):
        name (str | Unset):
        start_tariff (float | Unset):
        price (float | Unset):
        price_incl_vat (float | Unset):
        currency (str | Unset):
        last_updated (datetime.datetime | Unset):
        usage_type (TariffDtoUsageType | Unset):  Default: TariffDtoUsageType.SELL.
        tariff_type (TariffDtoTariffType | Unset):  Default: TariffDtoTariffType.REGULAR.
        vat (float | Unset):
        is_vat_relevant (bool | Unset):
        country_code (str | Unset):
        party_id (str | Unset):
        location_id (str | Unset):
        is_private_emp_tariff (bool | Unset):
        private_emp_tariff (PrivateEmpTariffDto | Unset):
        parking_tariff (float | Unset):
        parking_step_size_in_minutes (int | Unset):
        parking_grace_period_in_minutes (int | Unset):
        parking_tariff_restrictions (list[TariffRestriction] | Unset):
        parking_always_active_after_in_minutes (int | Unset):
        time_tariff (float | Unset):
        time_step_size_in_minutes (int | Unset):
        time_grace_period_in_minutes (int | Unset):
        price_history (list[TariffPriceDto] | Unset):
        external_reference (str | Unset):
        deleted (datetime.datetime | Unset):
        reimburse_type (TariffDtoReimburseType | Unset):  Default: TariffDtoReimburseType.ORGANIZATIONUNIT.
        reimburse_tokens (list[ReimburseToken] | Unset):
        ou (str | Unset):
        ou_id (str | Unset):
        ou_name (str | Unset):
        pricing_elements (list[PricingElement] | Unset):
    """

    tenant_id: str
    id: str | Unset = UNSET
    ocpi_id: str | Unset = UNSET
    hubject_id: str | Unset = UNSET
    name: str | Unset = UNSET
    start_tariff: float | Unset = UNSET
    price: float | Unset = UNSET
    price_incl_vat: float | Unset = UNSET
    currency: str | Unset = UNSET
    last_updated: datetime.datetime | Unset = UNSET
    usage_type: TariffDtoUsageType | Unset = TariffDtoUsageType.SELL
    tariff_type: TariffDtoTariffType | Unset = TariffDtoTariffType.REGULAR
    vat: float | Unset = UNSET
    is_vat_relevant: bool | Unset = UNSET
    country_code: str | Unset = UNSET
    party_id: str | Unset = UNSET
    location_id: str | Unset = UNSET
    is_private_emp_tariff: bool | Unset = UNSET
    private_emp_tariff: PrivateEmpTariffDto | Unset = UNSET
    parking_tariff: float | Unset = UNSET
    parking_step_size_in_minutes: int | Unset = UNSET
    parking_grace_period_in_minutes: int | Unset = UNSET
    parking_tariff_restrictions: list[TariffRestriction] | Unset = UNSET
    parking_always_active_after_in_minutes: int | Unset = UNSET
    time_tariff: float | Unset = UNSET
    time_step_size_in_minutes: int | Unset = UNSET
    time_grace_period_in_minutes: int | Unset = UNSET
    price_history: list[TariffPriceDto] | Unset = UNSET
    external_reference: str | Unset = UNSET
    deleted: datetime.datetime | Unset = UNSET
    reimburse_type: TariffDtoReimburseType | Unset = TariffDtoReimburseType.ORGANIZATIONUNIT
    reimburse_tokens: list[ReimburseToken] | Unset = UNSET
    ou: str | Unset = UNSET
    ou_id: str | Unset = UNSET
    ou_name: str | Unset = UNSET
    pricing_elements: list[PricingElement] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tenant_id = self.tenant_id

        id = self.id

        ocpi_id = self.ocpi_id

        hubject_id = self.hubject_id

        name = self.name

        start_tariff = self.start_tariff

        price = self.price

        price_incl_vat = self.price_incl_vat

        currency = self.currency

        last_updated: str | Unset = UNSET
        if not isinstance(self.last_updated, Unset):
            last_updated = self.last_updated.isoformat()

        usage_type: str | Unset = UNSET
        if not isinstance(self.usage_type, Unset):
            usage_type = self.usage_type.value

        tariff_type: str | Unset = UNSET
        if not isinstance(self.tariff_type, Unset):
            tariff_type = self.tariff_type.value

        vat = self.vat

        is_vat_relevant = self.is_vat_relevant

        country_code = self.country_code

        party_id = self.party_id

        location_id = self.location_id

        is_private_emp_tariff = self.is_private_emp_tariff

        private_emp_tariff: dict[str, Any] | Unset = UNSET
        if not isinstance(self.private_emp_tariff, Unset):
            private_emp_tariff = self.private_emp_tariff.to_dict()

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

        price_history: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.price_history, Unset):
            price_history = []
            for price_history_item_data in self.price_history:
                price_history_item = price_history_item_data.to_dict()
                price_history.append(price_history_item)

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
        field_dict.update(
            {
                "tenantId": tenant_id,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if ocpi_id is not UNSET:
            field_dict["ocpiId"] = ocpi_id
        if hubject_id is not UNSET:
            field_dict["hubjectId"] = hubject_id
        if name is not UNSET:
            field_dict["name"] = name
        if start_tariff is not UNSET:
            field_dict["startTariff"] = start_tariff
        if price is not UNSET:
            field_dict["price"] = price
        if price_incl_vat is not UNSET:
            field_dict["priceInclVat"] = price_incl_vat
        if currency is not UNSET:
            field_dict["currency"] = currency
        if last_updated is not UNSET:
            field_dict["last_updated"] = last_updated
        if usage_type is not UNSET:
            field_dict["usageType"] = usage_type
        if tariff_type is not UNSET:
            field_dict["tariffType"] = tariff_type
        if vat is not UNSET:
            field_dict["vat"] = vat
        if is_vat_relevant is not UNSET:
            field_dict["isVatRelevant"] = is_vat_relevant
        if country_code is not UNSET:
            field_dict["country_code"] = country_code
        if party_id is not UNSET:
            field_dict["party_id"] = party_id
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if is_private_emp_tariff is not UNSET:
            field_dict["isPrivateEmpTariff"] = is_private_emp_tariff
        if private_emp_tariff is not UNSET:
            field_dict["privateEmpTariff"] = private_emp_tariff
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
        if price_history is not UNSET:
            field_dict["priceHistory"] = price_history
        if external_reference is not UNSET:
            field_dict["externalReference"] = external_reference
        if deleted is not UNSET:
            field_dict["deleted"] = deleted
        if reimburse_type is not UNSET:
            field_dict["reimburseType"] = reimburse_type
        if reimburse_tokens is not UNSET:
            field_dict["reimburseTokens"] = reimburse_tokens
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
        from ..models.tariff_price_dto import TariffPriceDto
        from ..models.tariff_restriction import TariffRestriction

        d = dict(src_dict)
        tenant_id = d.pop("tenantId")

        id = d.pop("id", UNSET)

        ocpi_id = d.pop("ocpiId", UNSET)

        hubject_id = d.pop("hubjectId", UNSET)

        name = d.pop("name", UNSET)

        start_tariff = d.pop("startTariff", UNSET)

        price = d.pop("price", UNSET)

        price_incl_vat = d.pop("priceInclVat", UNSET)

        currency = d.pop("currency", UNSET)

        _last_updated = d.pop("last_updated", UNSET)
        last_updated: datetime.datetime | Unset
        if isinstance(_last_updated, Unset) or _last_updated is None:
            last_updated = UNSET
        else:
            last_updated = isoparse(_last_updated)

        _usage_type = d.pop("usageType", UNSET)
        usage_type: TariffDtoUsageType | Unset
        if isinstance(_usage_type, Unset) or _usage_type is None:
            usage_type = UNSET
        else:
            usage_type = TariffDtoUsageType(_usage_type)

        _tariff_type = d.pop("tariffType", UNSET)
        tariff_type: TariffDtoTariffType | Unset
        if isinstance(_tariff_type, Unset) or _tariff_type is None:
            tariff_type = UNSET
        else:
            tariff_type = TariffDtoTariffType(_tariff_type)

        vat = d.pop("vat", UNSET)

        is_vat_relevant = d.pop("isVatRelevant", UNSET)

        country_code = d.pop("country_code", UNSET)

        party_id = d.pop("party_id", UNSET)

        location_id = d.pop("locationId", UNSET)

        is_private_emp_tariff = d.pop("isPrivateEmpTariff", UNSET)

        _private_emp_tariff = d.pop("privateEmpTariff", UNSET)
        private_emp_tariff: PrivateEmpTariffDto | Unset
        if isinstance(_private_emp_tariff, Unset) or _private_emp_tariff is None:
            private_emp_tariff = UNSET
        else:
            private_emp_tariff = PrivateEmpTariffDto.from_dict(_private_emp_tariff)

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

        price_history = []
        _price_history = d.pop("priceHistory", UNSET)
        for price_history_item_data in _price_history or []:
            price_history_item = TariffPriceDto.from_dict(price_history_item_data)

            price_history.append(price_history_item)

        external_reference = d.pop("externalReference", UNSET)

        _deleted = d.pop("deleted", UNSET)
        deleted: datetime.datetime | Unset
        if isinstance(_deleted, Unset) or _deleted is None:
            deleted = UNSET
        else:
            deleted = isoparse(_deleted)

        _reimburse_type = d.pop("reimburseType", UNSET)
        reimburse_type: TariffDtoReimburseType | Unset
        if isinstance(_reimburse_type, Unset) or _reimburse_type is None:
            reimburse_type = UNSET
        else:
            reimburse_type = TariffDtoReimburseType(_reimburse_type)

        reimburse_tokens = []
        _reimburse_tokens = d.pop("reimburseTokens", UNSET)
        for reimburse_tokens_item_data in _reimburse_tokens or []:
            reimburse_tokens_item = ReimburseToken.from_dict(reimburse_tokens_item_data)

            reimburse_tokens.append(reimburse_tokens_item)

        ou = d.pop("ou", UNSET)

        ou_id = d.pop("ouId", UNSET)

        ou_name = d.pop("ouName", UNSET)

        pricing_elements = []
        _pricing_elements = d.pop("pricingElements", UNSET)
        for pricing_elements_item_data in _pricing_elements or []:
            pricing_elements_item = PricingElement.from_dict(pricing_elements_item_data)

            pricing_elements.append(pricing_elements_item)

        tariff_dto = cls(
            tenant_id=tenant_id,
            id=id,
            ocpi_id=ocpi_id,
            hubject_id=hubject_id,
            name=name,
            start_tariff=start_tariff,
            price=price,
            price_incl_vat=price_incl_vat,
            currency=currency,
            last_updated=last_updated,
            usage_type=usage_type,
            tariff_type=tariff_type,
            vat=vat,
            is_vat_relevant=is_vat_relevant,
            country_code=country_code,
            party_id=party_id,
            location_id=location_id,
            is_private_emp_tariff=is_private_emp_tariff,
            private_emp_tariff=private_emp_tariff,
            parking_tariff=parking_tariff,
            parking_step_size_in_minutes=parking_step_size_in_minutes,
            parking_grace_period_in_minutes=parking_grace_period_in_minutes,
            parking_tariff_restrictions=parking_tariff_restrictions,
            parking_always_active_after_in_minutes=parking_always_active_after_in_minutes,
            time_tariff=time_tariff,
            time_step_size_in_minutes=time_step_size_in_minutes,
            time_grace_period_in_minutes=time_grace_period_in_minutes,
            price_history=price_history,
            external_reference=external_reference,
            deleted=deleted,
            reimburse_type=reimburse_type,
            reimburse_tokens=reimburse_tokens,
            ou=ou,
            ou_id=ou_id,
            ou_name=ou_name,
            pricing_elements=pricing_elements,
        )

        tariff_dto.additional_properties = d
        return tariff_dto

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

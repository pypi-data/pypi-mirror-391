from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.reimbursement_tariff_dto_tariff_type import ReimbursementTariffDtoTariffType
from ..models.reimbursement_tariff_dto_usage_type import ReimbursementTariffDtoUsageType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.tariff_price_dto import TariffPriceDto


T = TypeVar("T", bound="ReimbursementTariffDto")


@_attrs_define
class ReimbursementTariffDto:
    """
    Attributes:
        id (str | Unset):
        hubject_id (str | Unset):
        ocpi_id (str | Unset):
        tenant_id (str | Unset):
        name (str | Unset):
        price (float | Unset):
        country_code (str | Unset):
        currency (str | Unset):
        last_updated (datetime.datetime | Unset):
        party_id (str | Unset):
        tariff_type (ReimbursementTariffDtoTariffType | Unset):  Default: ReimbursementTariffDtoTariffType.REGULAR.
        usage_type (ReimbursementTariffDtoUsageType | Unset):  Default: ReimbursementTariffDtoUsageType.SELL.
        vat_percentage (float | Unset):
        location_id (str | Unset):
        is_vat_relevant (bool | Unset):
        price_incl_vat (float | Unset):
        external_reference (str | Unset):
        deleted (datetime.datetime | Unset):
        price_history (list[TariffPriceDto] | Unset):
    """

    id: str | Unset = UNSET
    hubject_id: str | Unset = UNSET
    ocpi_id: str | Unset = UNSET
    tenant_id: str | Unset = UNSET
    name: str | Unset = UNSET
    price: float | Unset = UNSET
    country_code: str | Unset = UNSET
    currency: str | Unset = UNSET
    last_updated: datetime.datetime | Unset = UNSET
    party_id: str | Unset = UNSET
    tariff_type: ReimbursementTariffDtoTariffType | Unset = ReimbursementTariffDtoTariffType.REGULAR
    usage_type: ReimbursementTariffDtoUsageType | Unset = ReimbursementTariffDtoUsageType.SELL
    vat_percentage: float | Unset = UNSET
    location_id: str | Unset = UNSET
    is_vat_relevant: bool | Unset = UNSET
    price_incl_vat: float | Unset = UNSET
    external_reference: str | Unset = UNSET
    deleted: datetime.datetime | Unset = UNSET
    price_history: list[TariffPriceDto] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        hubject_id = self.hubject_id

        ocpi_id = self.ocpi_id

        tenant_id = self.tenant_id

        name = self.name

        price = self.price

        country_code = self.country_code

        currency = self.currency

        last_updated: str | Unset = UNSET
        if not isinstance(self.last_updated, Unset):
            last_updated = self.last_updated.isoformat()

        party_id = self.party_id

        tariff_type: str | Unset = UNSET
        if not isinstance(self.tariff_type, Unset):
            tariff_type = self.tariff_type.value

        usage_type: str | Unset = UNSET
        if not isinstance(self.usage_type, Unset):
            usage_type = self.usage_type.value

        vat_percentage = self.vat_percentage

        location_id = self.location_id

        is_vat_relevant = self.is_vat_relevant

        price_incl_vat = self.price_incl_vat

        external_reference = self.external_reference

        deleted: str | Unset = UNSET
        if not isinstance(self.deleted, Unset):
            deleted = self.deleted.isoformat()

        price_history: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.price_history, Unset):
            price_history = []
            for price_history_item_data in self.price_history:
                price_history_item = price_history_item_data.to_dict()
                price_history.append(price_history_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if hubject_id is not UNSET:
            field_dict["hubjectId"] = hubject_id
        if ocpi_id is not UNSET:
            field_dict["ocpiId"] = ocpi_id
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if name is not UNSET:
            field_dict["name"] = name
        if price is not UNSET:
            field_dict["price"] = price
        if country_code is not UNSET:
            field_dict["countryCode"] = country_code
        if currency is not UNSET:
            field_dict["currency"] = currency
        if last_updated is not UNSET:
            field_dict["lastUpdated"] = last_updated
        if party_id is not UNSET:
            field_dict["partyId"] = party_id
        if tariff_type is not UNSET:
            field_dict["tariffType"] = tariff_type
        if usage_type is not UNSET:
            field_dict["usageType"] = usage_type
        if vat_percentage is not UNSET:
            field_dict["vatPercentage"] = vat_percentage
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if is_vat_relevant is not UNSET:
            field_dict["isVatRelevant"] = is_vat_relevant
        if price_incl_vat is not UNSET:
            field_dict["priceInclVat"] = price_incl_vat
        if external_reference is not UNSET:
            field_dict["externalReference"] = external_reference
        if deleted is not UNSET:
            field_dict["deleted"] = deleted
        if price_history is not UNSET:
            field_dict["priceHistory"] = price_history

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tariff_price_dto import TariffPriceDto

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        hubject_id = d.pop("hubjectId", UNSET)

        ocpi_id = d.pop("ocpiId", UNSET)

        tenant_id = d.pop("tenantId", UNSET)

        name = d.pop("name", UNSET)

        price = d.pop("price", UNSET)

        country_code = d.pop("countryCode", UNSET)

        currency = d.pop("currency", UNSET)

        _last_updated = d.pop("lastUpdated", UNSET)
        last_updated: datetime.datetime | Unset
        if isinstance(_last_updated, Unset) or _last_updated is None:
            last_updated = UNSET
        else:
            last_updated = isoparse(_last_updated)

        party_id = d.pop("partyId", UNSET)

        _tariff_type = d.pop("tariffType", UNSET)
        tariff_type: ReimbursementTariffDtoTariffType | Unset
        if isinstance(_tariff_type, Unset) or _tariff_type is None:
            tariff_type = UNSET
        else:
            tariff_type = ReimbursementTariffDtoTariffType(_tariff_type)

        _usage_type = d.pop("usageType", UNSET)
        usage_type: ReimbursementTariffDtoUsageType | Unset
        if isinstance(_usage_type, Unset) or _usage_type is None:
            usage_type = UNSET
        else:
            usage_type = ReimbursementTariffDtoUsageType(_usage_type)

        vat_percentage = d.pop("vatPercentage", UNSET)

        location_id = d.pop("locationId", UNSET)

        is_vat_relevant = d.pop("isVatRelevant", UNSET)

        price_incl_vat = d.pop("priceInclVat", UNSET)

        external_reference = d.pop("externalReference", UNSET)

        _deleted = d.pop("deleted", UNSET)
        deleted: datetime.datetime | Unset
        if isinstance(_deleted, Unset) or _deleted is None:
            deleted = UNSET
        else:
            deleted = isoparse(_deleted)

        price_history = []
        _price_history = d.pop("priceHistory", UNSET)
        for price_history_item_data in _price_history or []:
            price_history_item = TariffPriceDto.from_dict(price_history_item_data)

            price_history.append(price_history_item)

        reimbursement_tariff_dto = cls(
            id=id,
            hubject_id=hubject_id,
            ocpi_id=ocpi_id,
            tenant_id=tenant_id,
            name=name,
            price=price,
            country_code=country_code,
            currency=currency,
            last_updated=last_updated,
            party_id=party_id,
            tariff_type=tariff_type,
            usage_type=usage_type,
            vat_percentage=vat_percentage,
            location_id=location_id,
            is_vat_relevant=is_vat_relevant,
            price_incl_vat=price_incl_vat,
            external_reference=external_reference,
            deleted=deleted,
            price_history=price_history,
        )

        reimbursement_tariff_dto.additional_properties = d
        return reimbursement_tariff_dto

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

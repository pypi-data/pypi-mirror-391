from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.dynamic_tariff_get_dto_tariff_type import DynamicTariffGetDtoTariffType
from ..types import UNSET, Unset

T = TypeVar("T", bound="DynamicTariffGetDto")


@_attrs_define
class DynamicTariffGetDto:
    """
    Attributes:
        id (str):
        name (str):
        ou_code (str):
        currency (str):
        tariff_type (DynamicTariffGetDtoTariffType):  Default: DynamicTariffGetDtoTariffType.REGULAR.
        country (str):
        fallback_kwh_tariff (float):
        time_zone (str):
        source_id (str):
        history_id (str):
        valid_from (datetime.datetime):
        created (datetime.datetime):
        modified (datetime.datetime | Unset):
        deleted (datetime.datetime | Unset):
        max_kwh_tariff (float | Unset):
        min_kwh_tariff (float | Unset):
        fixed_margin (float | Unset):
        ocpi_id (str | Unset):
        hubject_id (str | Unset):
        sequence_number (int | Unset):
        external_reference (str | Unset):
        party_id (str | Unset):
        country_id (str | Unset):
    """

    id: str
    name: str
    ou_code: str
    currency: str
    country: str
    fallback_kwh_tariff: float
    time_zone: str
    source_id: str
    history_id: str
    valid_from: datetime.datetime
    created: datetime.datetime
    tariff_type: DynamicTariffGetDtoTariffType = DynamicTariffGetDtoTariffType.REGULAR
    modified: datetime.datetime | Unset = UNSET
    deleted: datetime.datetime | Unset = UNSET
    max_kwh_tariff: float | Unset = UNSET
    min_kwh_tariff: float | Unset = UNSET
    fixed_margin: float | Unset = UNSET
    ocpi_id: str | Unset = UNSET
    hubject_id: str | Unset = UNSET
    sequence_number: int | Unset = UNSET
    external_reference: str | Unset = UNSET
    party_id: str | Unset = UNSET
    country_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        ou_code = self.ou_code

        currency = self.currency

        tariff_type = self.tariff_type.value

        country = self.country

        fallback_kwh_tariff = self.fallback_kwh_tariff

        time_zone = self.time_zone

        source_id = self.source_id

        history_id = self.history_id

        valid_from = self.valid_from.isoformat()

        created = self.created.isoformat()

        modified: str | Unset = UNSET
        if not isinstance(self.modified, Unset):
            modified = self.modified.isoformat()

        deleted: str | Unset = UNSET
        if not isinstance(self.deleted, Unset):
            deleted = self.deleted.isoformat()

        max_kwh_tariff = self.max_kwh_tariff

        min_kwh_tariff = self.min_kwh_tariff

        fixed_margin = self.fixed_margin

        ocpi_id = self.ocpi_id

        hubject_id = self.hubject_id

        sequence_number = self.sequence_number

        external_reference = self.external_reference

        party_id = self.party_id

        country_id = self.country_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "ouCode": ou_code,
                "currency": currency,
                "tariffType": tariff_type,
                "country": country,
                "fallbackKwhTariff": fallback_kwh_tariff,
                "timeZone": time_zone,
                "sourceId": source_id,
                "historyId": history_id,
                "validFrom": valid_from,
                "created": created,
            }
        )
        if modified is not UNSET:
            field_dict["modified"] = modified
        if deleted is not UNSET:
            field_dict["deleted"] = deleted
        if max_kwh_tariff is not UNSET:
            field_dict["maxKwhTariff"] = max_kwh_tariff
        if min_kwh_tariff is not UNSET:
            field_dict["minKwhTariff"] = min_kwh_tariff
        if fixed_margin is not UNSET:
            field_dict["fixedMargin"] = fixed_margin
        if ocpi_id is not UNSET:
            field_dict["ocpiId"] = ocpi_id
        if hubject_id is not UNSET:
            field_dict["hubjectId"] = hubject_id
        if sequence_number is not UNSET:
            field_dict["sequenceNumber"] = sequence_number
        if external_reference is not UNSET:
            field_dict["externalReference"] = external_reference
        if party_id is not UNSET:
            field_dict["partyId"] = party_id
        if country_id is not UNSET:
            field_dict["countryId"] = country_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        ou_code = d.pop("ouCode")

        currency = d.pop("currency")

        tariff_type = DynamicTariffGetDtoTariffType(d.pop("tariffType"))

        country = d.pop("country")

        fallback_kwh_tariff = d.pop("fallbackKwhTariff")

        time_zone = d.pop("timeZone")

        source_id = d.pop("sourceId")

        history_id = d.pop("historyId")

        valid_from = isoparse(d.pop("validFrom"))

        created = isoparse(d.pop("created"))

        _modified = d.pop("modified", UNSET)
        modified: datetime.datetime | Unset
        if isinstance(_modified, Unset) or _modified is None:
            modified = UNSET
        else:
            modified = isoparse(_modified)

        _deleted = d.pop("deleted", UNSET)
        deleted: datetime.datetime | Unset
        if isinstance(_deleted, Unset) or _deleted is None:
            deleted = UNSET
        else:
            deleted = isoparse(_deleted)

        max_kwh_tariff = d.pop("maxKwhTariff", UNSET)

        min_kwh_tariff = d.pop("minKwhTariff", UNSET)

        fixed_margin = d.pop("fixedMargin", UNSET)

        ocpi_id = d.pop("ocpiId", UNSET)

        hubject_id = d.pop("hubjectId", UNSET)

        sequence_number = d.pop("sequenceNumber", UNSET)

        external_reference = d.pop("externalReference", UNSET)

        party_id = d.pop("partyId", UNSET)

        country_id = d.pop("countryId", UNSET)

        dynamic_tariff_get_dto = cls(
            id=id,
            name=name,
            ou_code=ou_code,
            currency=currency,
            tariff_type=tariff_type,
            country=country,
            fallback_kwh_tariff=fallback_kwh_tariff,
            time_zone=time_zone,
            source_id=source_id,
            history_id=history_id,
            valid_from=valid_from,
            created=created,
            modified=modified,
            deleted=deleted,
            max_kwh_tariff=max_kwh_tariff,
            min_kwh_tariff=min_kwh_tariff,
            fixed_margin=fixed_margin,
            ocpi_id=ocpi_id,
            hubject_id=hubject_id,
            sequence_number=sequence_number,
            external_reference=external_reference,
            party_id=party_id,
            country_id=country_id,
        )

        dynamic_tariff_get_dto.additional_properties = d
        return dynamic_tariff_get_dto

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

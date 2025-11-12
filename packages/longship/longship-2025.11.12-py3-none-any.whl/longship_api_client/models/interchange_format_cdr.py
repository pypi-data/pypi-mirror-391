from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="InterchangeFormatCdr")


@_attrs_define
class InterchangeFormatCdr:
    """
    Attributes:
        cdr_id (str | Unset):
        start_date_time (datetime.datetime | Unset):
        end_date_time (datetime.datetime | Unset):
        duration (str | Unset):
        volume (float | Unset):
        charge_point_address (str | Unset):
        charge_point_zip (str | Unset):
        charge_point_city (str | Unset):
        charge_point_country (str | Unset):
        charge_point_type (str | Unset):
        product_type (str | Unset):
        tariff_type (str | Unset):
        authentication_id (str | Unset):
        contract_id (str | Unset):
        meter_id (str | Unset):
        obis_code (str | Unset):
        charge_point_id (str | Unset):
        service_provider_id (str | Unset):
        infra_provider_id (str | Unset):
        calculated_cost (float | Unset):
    """

    cdr_id: str | Unset = UNSET
    start_date_time: datetime.datetime | Unset = UNSET
    end_date_time: datetime.datetime | Unset = UNSET
    duration: str | Unset = UNSET
    volume: float | Unset = UNSET
    charge_point_address: str | Unset = UNSET
    charge_point_zip: str | Unset = UNSET
    charge_point_city: str | Unset = UNSET
    charge_point_country: str | Unset = UNSET
    charge_point_type: str | Unset = UNSET
    product_type: str | Unset = UNSET
    tariff_type: str | Unset = UNSET
    authentication_id: str | Unset = UNSET
    contract_id: str | Unset = UNSET
    meter_id: str | Unset = UNSET
    obis_code: str | Unset = UNSET
    charge_point_id: str | Unset = UNSET
    service_provider_id: str | Unset = UNSET
    infra_provider_id: str | Unset = UNSET
    calculated_cost: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cdr_id = self.cdr_id

        start_date_time: str | Unset = UNSET
        if not isinstance(self.start_date_time, Unset):
            start_date_time = self.start_date_time.isoformat()

        end_date_time: str | Unset = UNSET
        if not isinstance(self.end_date_time, Unset):
            end_date_time = self.end_date_time.isoformat()

        duration = self.duration

        volume = self.volume

        charge_point_address = self.charge_point_address

        charge_point_zip = self.charge_point_zip

        charge_point_city = self.charge_point_city

        charge_point_country = self.charge_point_country

        charge_point_type = self.charge_point_type

        product_type = self.product_type

        tariff_type = self.tariff_type

        authentication_id = self.authentication_id

        contract_id = self.contract_id

        meter_id = self.meter_id

        obis_code = self.obis_code

        charge_point_id = self.charge_point_id

        service_provider_id = self.service_provider_id

        infra_provider_id = self.infra_provider_id

        calculated_cost = self.calculated_cost

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cdr_id is not UNSET:
            field_dict["cdrId"] = cdr_id
        if start_date_time is not UNSET:
            field_dict["startDateTime"] = start_date_time
        if end_date_time is not UNSET:
            field_dict["endDateTime"] = end_date_time
        if duration is not UNSET:
            field_dict["duration"] = duration
        if volume is not UNSET:
            field_dict["volume"] = volume
        if charge_point_address is not UNSET:
            field_dict["chargePointAddress"] = charge_point_address
        if charge_point_zip is not UNSET:
            field_dict["chargePointZip"] = charge_point_zip
        if charge_point_city is not UNSET:
            field_dict["chargePointCity"] = charge_point_city
        if charge_point_country is not UNSET:
            field_dict["chargePointCountry"] = charge_point_country
        if charge_point_type is not UNSET:
            field_dict["chargePointType"] = charge_point_type
        if product_type is not UNSET:
            field_dict["productType"] = product_type
        if tariff_type is not UNSET:
            field_dict["tariffType"] = tariff_type
        if authentication_id is not UNSET:
            field_dict["authenticationId"] = authentication_id
        if contract_id is not UNSET:
            field_dict["contractId"] = contract_id
        if meter_id is not UNSET:
            field_dict["meterId"] = meter_id
        if obis_code is not UNSET:
            field_dict["obisCode"] = obis_code
        if charge_point_id is not UNSET:
            field_dict["chargePointId"] = charge_point_id
        if service_provider_id is not UNSET:
            field_dict["serviceProviderId"] = service_provider_id
        if infra_provider_id is not UNSET:
            field_dict["infraProviderId"] = infra_provider_id
        if calculated_cost is not UNSET:
            field_dict["calculatedCost"] = calculated_cost

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        cdr_id = d.pop("cdrId", UNSET)

        _start_date_time = d.pop("startDateTime", UNSET)
        start_date_time: datetime.datetime | Unset
        if isinstance(_start_date_time, Unset) or _start_date_time is None:
            start_date_time = UNSET
        else:
            start_date_time = isoparse(_start_date_time)

        _end_date_time = d.pop("endDateTime", UNSET)
        end_date_time: datetime.datetime | Unset
        if isinstance(_end_date_time, Unset) or _end_date_time is None:
            end_date_time = UNSET
        else:
            end_date_time = isoparse(_end_date_time)

        duration = d.pop("duration", UNSET)

        volume = d.pop("volume", UNSET)

        charge_point_address = d.pop("chargePointAddress", UNSET)

        charge_point_zip = d.pop("chargePointZip", UNSET)

        charge_point_city = d.pop("chargePointCity", UNSET)

        charge_point_country = d.pop("chargePointCountry", UNSET)

        charge_point_type = d.pop("chargePointType", UNSET)

        product_type = d.pop("productType", UNSET)

        tariff_type = d.pop("tariffType", UNSET)

        authentication_id = d.pop("authenticationId", UNSET)

        contract_id = d.pop("contractId", UNSET)

        meter_id = d.pop("meterId", UNSET)

        obis_code = d.pop("obisCode", UNSET)

        charge_point_id = d.pop("chargePointId", UNSET)

        service_provider_id = d.pop("serviceProviderId", UNSET)

        infra_provider_id = d.pop("infraProviderId", UNSET)

        calculated_cost = d.pop("calculatedCost", UNSET)

        interchange_format_cdr = cls(
            cdr_id=cdr_id,
            start_date_time=start_date_time,
            end_date_time=end_date_time,
            duration=duration,
            volume=volume,
            charge_point_address=charge_point_address,
            charge_point_zip=charge_point_zip,
            charge_point_city=charge_point_city,
            charge_point_country=charge_point_country,
            charge_point_type=charge_point_type,
            product_type=product_type,
            tariff_type=tariff_type,
            authentication_id=authentication_id,
            contract_id=contract_id,
            meter_id=meter_id,
            obis_code=obis_code,
            charge_point_id=charge_point_id,
            service_provider_id=service_provider_id,
            infra_provider_id=infra_provider_id,
            calculated_cost=calculated_cost,
        )

        interchange_format_cdr.additional_properties = d
        return interchange_format_cdr

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

from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.ou_integration_info_dto import OuIntegrationInfoDto
    from ..models.price_info_dto import PriceInfoDto
    from ..models.reimburse_started_by_info_dto import ReimburseStartedByInfoDto
    from ..models.reimbursement_cdr_location_dto import ReimbursementCdrLocationDto
    from ..models.reimbursement_customer_share_dto import ReimbursementCustomerShareDto


T = TypeVar("T", bound="ReimbursementCdrDto")


@_attrs_define
class ReimbursementCdrDto:
    """
    Attributes:
        id (str | Unset):
        tenant_id (str | Unset):
        charge_point_id (str | Unset):
        connector_id (int | Unset):
        location_id (str | Unset):
        evse_id (str | Unset):
        location (ReimbursementCdrLocationDto | Unset):
        start_datetime (datetime.datetime | Unset):
        end_date_time (datetime.datetime | Unset):
        session_id (str | Unset):
        started_by_info (ReimburseStartedByInfoDto | Unset):
        meter_start_in_wh (int | Unset):
        meter_stop_in_wh (int | Unset):
        total_energy_in_kwh (float | Unset):
        total_time_in_hours (float | Unset):
        total_price (float | Unset):
        created (datetime.datetime | Unset):
        last_updated (datetime.datetime | Unset):
        ou (str | Unset):
        ou_id (str | Unset):
        ou_name (str | Unset):
        reimburse_tariff_id (str | Unset):
        reimburse_tariff_name (str | Unset):
        reimburse_tariff_price (float | Unset):
        reimburse_tariff_calculated (bool | Unset):
        reimburse_price_calculated_on (datetime.datetime | Unset):
        bank_account (str | Unset):
        bank_account_created_on (datetime.datetime | Unset):
        bank_account_valid_from (datetime.datetime | Unset):
        reimburse_tariff_original_price (float | Unset):
        has_guest_charging_reimbursement_fee (bool | Unset):
        reimburse_tenant_fee (float | Unset):
        tenant_fee_calculated (bool | Unset):
        tariff_distribution_id (str | Unset):
        price_info (PriceInfoDto | Unset):
        customer_share (float | Unset):
        energy_compensation (float | Unset):
        reimbursement_customer_share (ReimbursementCustomerShareDto | Unset):
        local_start_date_time (datetime.datetime | Unset):
        local_end_date_time (datetime.datetime | Unset):
        ou_integration_info (OuIntegrationInfoDto | Unset):
    """

    id: str | Unset = UNSET
    tenant_id: str | Unset = UNSET
    charge_point_id: str | Unset = UNSET
    connector_id: int | Unset = UNSET
    location_id: str | Unset = UNSET
    evse_id: str | Unset = UNSET
    location: ReimbursementCdrLocationDto | Unset = UNSET
    start_datetime: datetime.datetime | Unset = UNSET
    end_date_time: datetime.datetime | Unset = UNSET
    session_id: str | Unset = UNSET
    started_by_info: ReimburseStartedByInfoDto | Unset = UNSET
    meter_start_in_wh: int | Unset = UNSET
    meter_stop_in_wh: int | Unset = UNSET
    total_energy_in_kwh: float | Unset = UNSET
    total_time_in_hours: float | Unset = UNSET
    total_price: float | Unset = UNSET
    created: datetime.datetime | Unset = UNSET
    last_updated: datetime.datetime | Unset = UNSET
    ou: str | Unset = UNSET
    ou_id: str | Unset = UNSET
    ou_name: str | Unset = UNSET
    reimburse_tariff_id: str | Unset = UNSET
    reimburse_tariff_name: str | Unset = UNSET
    reimburse_tariff_price: float | Unset = UNSET
    reimburse_tariff_calculated: bool | Unset = UNSET
    reimburse_price_calculated_on: datetime.datetime | Unset = UNSET
    bank_account: str | Unset = UNSET
    bank_account_created_on: datetime.datetime | Unset = UNSET
    bank_account_valid_from: datetime.datetime | Unset = UNSET
    reimburse_tariff_original_price: float | Unset = UNSET
    has_guest_charging_reimbursement_fee: bool | Unset = UNSET
    reimburse_tenant_fee: float | Unset = UNSET
    tenant_fee_calculated: bool | Unset = UNSET
    tariff_distribution_id: str | Unset = UNSET
    price_info: PriceInfoDto | Unset = UNSET
    customer_share: float | Unset = UNSET
    energy_compensation: float | Unset = UNSET
    reimbursement_customer_share: ReimbursementCustomerShareDto | Unset = UNSET
    local_start_date_time: datetime.datetime | Unset = UNSET
    local_end_date_time: datetime.datetime | Unset = UNSET
    ou_integration_info: OuIntegrationInfoDto | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        tenant_id = self.tenant_id

        charge_point_id = self.charge_point_id

        connector_id = self.connector_id

        location_id = self.location_id

        evse_id = self.evse_id

        location: dict[str, Any] | Unset = UNSET
        if not isinstance(self.location, Unset):
            location = self.location.to_dict()

        start_datetime: str | Unset = UNSET
        if not isinstance(self.start_datetime, Unset):
            start_datetime = self.start_datetime.isoformat()

        end_date_time: str | Unset = UNSET
        if not isinstance(self.end_date_time, Unset):
            end_date_time = self.end_date_time.isoformat()

        session_id = self.session_id

        started_by_info: dict[str, Any] | Unset = UNSET
        if not isinstance(self.started_by_info, Unset):
            started_by_info = self.started_by_info.to_dict()

        meter_start_in_wh = self.meter_start_in_wh

        meter_stop_in_wh = self.meter_stop_in_wh

        total_energy_in_kwh = self.total_energy_in_kwh

        total_time_in_hours = self.total_time_in_hours

        total_price = self.total_price

        created: str | Unset = UNSET
        if not isinstance(self.created, Unset):
            created = self.created.isoformat()

        last_updated: str | Unset = UNSET
        if not isinstance(self.last_updated, Unset):
            last_updated = self.last_updated.isoformat()

        ou = self.ou

        ou_id = self.ou_id

        ou_name = self.ou_name

        reimburse_tariff_id = self.reimburse_tariff_id

        reimburse_tariff_name = self.reimburse_tariff_name

        reimburse_tariff_price = self.reimburse_tariff_price

        reimburse_tariff_calculated = self.reimburse_tariff_calculated

        reimburse_price_calculated_on: str | Unset = UNSET
        if not isinstance(self.reimburse_price_calculated_on, Unset):
            reimburse_price_calculated_on = self.reimburse_price_calculated_on.isoformat()

        bank_account = self.bank_account

        bank_account_created_on: str | Unset = UNSET
        if not isinstance(self.bank_account_created_on, Unset):
            bank_account_created_on = self.bank_account_created_on.isoformat()

        bank_account_valid_from: str | Unset = UNSET
        if not isinstance(self.bank_account_valid_from, Unset):
            bank_account_valid_from = self.bank_account_valid_from.isoformat()

        reimburse_tariff_original_price = self.reimburse_tariff_original_price

        has_guest_charging_reimbursement_fee = self.has_guest_charging_reimbursement_fee

        reimburse_tenant_fee = self.reimburse_tenant_fee

        tenant_fee_calculated = self.tenant_fee_calculated

        tariff_distribution_id = self.tariff_distribution_id

        price_info: dict[str, Any] | Unset = UNSET
        if not isinstance(self.price_info, Unset):
            price_info = self.price_info.to_dict()

        customer_share = self.customer_share

        energy_compensation = self.energy_compensation

        reimbursement_customer_share: dict[str, Any] | Unset = UNSET
        if not isinstance(self.reimbursement_customer_share, Unset):
            reimbursement_customer_share = self.reimbursement_customer_share.to_dict()

        local_start_date_time: str | Unset = UNSET
        if not isinstance(self.local_start_date_time, Unset):
            local_start_date_time = self.local_start_date_time.isoformat()

        local_end_date_time: str | Unset = UNSET
        if not isinstance(self.local_end_date_time, Unset):
            local_end_date_time = self.local_end_date_time.isoformat()

        ou_integration_info: dict[str, Any] | Unset = UNSET
        if not isinstance(self.ou_integration_info, Unset):
            ou_integration_info = self.ou_integration_info.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if charge_point_id is not UNSET:
            field_dict["chargePointId"] = charge_point_id
        if connector_id is not UNSET:
            field_dict["connectorId"] = connector_id
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if evse_id is not UNSET:
            field_dict["evseId"] = evse_id
        if location is not UNSET:
            field_dict["location"] = location
        if start_datetime is not UNSET:
            field_dict["startDatetime"] = start_datetime
        if end_date_time is not UNSET:
            field_dict["endDateTime"] = end_date_time
        if session_id is not UNSET:
            field_dict["sessionId"] = session_id
        if started_by_info is not UNSET:
            field_dict["startedByInfo"] = started_by_info
        if meter_start_in_wh is not UNSET:
            field_dict["meterStartInWh"] = meter_start_in_wh
        if meter_stop_in_wh is not UNSET:
            field_dict["meterStopInWh"] = meter_stop_in_wh
        if total_energy_in_kwh is not UNSET:
            field_dict["totalEnergyInKwh"] = total_energy_in_kwh
        if total_time_in_hours is not UNSET:
            field_dict["totalTimeInHours"] = total_time_in_hours
        if total_price is not UNSET:
            field_dict["totalPrice"] = total_price
        if created is not UNSET:
            field_dict["created"] = created
        if last_updated is not UNSET:
            field_dict["lastUpdated"] = last_updated
        if ou is not UNSET:
            field_dict["ou"] = ou
        if ou_id is not UNSET:
            field_dict["ouId"] = ou_id
        if ou_name is not UNSET:
            field_dict["ouName"] = ou_name
        if reimburse_tariff_id is not UNSET:
            field_dict["reimburseTariffId"] = reimburse_tariff_id
        if reimburse_tariff_name is not UNSET:
            field_dict["reimburseTariffName"] = reimburse_tariff_name
        if reimburse_tariff_price is not UNSET:
            field_dict["reimburseTariffPrice"] = reimburse_tariff_price
        if reimburse_tariff_calculated is not UNSET:
            field_dict["reimburseTariffCalculated"] = reimburse_tariff_calculated
        if reimburse_price_calculated_on is not UNSET:
            field_dict["reimbursePriceCalculatedOn"] = reimburse_price_calculated_on
        if bank_account is not UNSET:
            field_dict["bankAccount"] = bank_account
        if bank_account_created_on is not UNSET:
            field_dict["bankAccountCreatedOn"] = bank_account_created_on
        if bank_account_valid_from is not UNSET:
            field_dict["bankAccountValidFrom"] = bank_account_valid_from
        if reimburse_tariff_original_price is not UNSET:
            field_dict["reimburseTariffOriginalPrice"] = reimburse_tariff_original_price
        if has_guest_charging_reimbursement_fee is not UNSET:
            field_dict["hasGuestChargingReimbursementFee"] = has_guest_charging_reimbursement_fee
        if reimburse_tenant_fee is not UNSET:
            field_dict["reimburseTenantFee"] = reimburse_tenant_fee
        if tenant_fee_calculated is not UNSET:
            field_dict["tenantFeeCalculated"] = tenant_fee_calculated
        if tariff_distribution_id is not UNSET:
            field_dict["tariffDistributionId"] = tariff_distribution_id
        if price_info is not UNSET:
            field_dict["priceInfo"] = price_info
        if customer_share is not UNSET:
            field_dict["customerShare"] = customer_share
        if energy_compensation is not UNSET:
            field_dict["energyCompensation"] = energy_compensation
        if reimbursement_customer_share is not UNSET:
            field_dict["reimbursementCustomerShare"] = reimbursement_customer_share
        if local_start_date_time is not UNSET:
            field_dict["localStartDateTime"] = local_start_date_time
        if local_end_date_time is not UNSET:
            field_dict["localEndDateTime"] = local_end_date_time
        if ou_integration_info is not UNSET:
            field_dict["ouIntegrationInfo"] = ou_integration_info

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.ou_integration_info_dto import OuIntegrationInfoDto
        from ..models.price_info_dto import PriceInfoDto
        from ..models.reimburse_started_by_info_dto import ReimburseStartedByInfoDto
        from ..models.reimbursement_cdr_location_dto import ReimbursementCdrLocationDto
        from ..models.reimbursement_customer_share_dto import ReimbursementCustomerShareDto

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        tenant_id = d.pop("tenantId", UNSET)

        charge_point_id = d.pop("chargePointId", UNSET)

        connector_id = d.pop("connectorId", UNSET)

        location_id = d.pop("locationId", UNSET)

        evse_id = d.pop("evseId", UNSET)

        _location = d.pop("location", UNSET)
        location: ReimbursementCdrLocationDto | Unset
        if isinstance(_location, Unset) or _location is None:
            location = UNSET
        else:
            location = ReimbursementCdrLocationDto.from_dict(_location)

        _start_datetime = d.pop("startDatetime", UNSET)
        start_datetime: datetime.datetime | Unset
        if isinstance(_start_datetime, Unset) or _start_datetime is None:
            start_datetime = UNSET
        else:
            start_datetime = isoparse(_start_datetime)

        _end_date_time = d.pop("endDateTime", UNSET)
        end_date_time: datetime.datetime | Unset
        if isinstance(_end_date_time, Unset) or _end_date_time is None:
            end_date_time = UNSET
        else:
            end_date_time = isoparse(_end_date_time)

        session_id = d.pop("sessionId", UNSET)

        _started_by_info = d.pop("startedByInfo", UNSET)
        started_by_info: ReimburseStartedByInfoDto | Unset
        if isinstance(_started_by_info, Unset) or _started_by_info is None:
            started_by_info = UNSET
        else:
            started_by_info = ReimburseStartedByInfoDto.from_dict(_started_by_info)

        meter_start_in_wh = d.pop("meterStartInWh", UNSET)

        meter_stop_in_wh = d.pop("meterStopInWh", UNSET)

        total_energy_in_kwh = d.pop("totalEnergyInKwh", UNSET)

        total_time_in_hours = d.pop("totalTimeInHours", UNSET)

        total_price = d.pop("totalPrice", UNSET)

        _created = d.pop("created", UNSET)
        created: datetime.datetime | Unset
        if isinstance(_created, Unset) or _created is None:
            created = UNSET
        else:
            created = isoparse(_created)

        _last_updated = d.pop("lastUpdated", UNSET)
        last_updated: datetime.datetime | Unset
        if isinstance(_last_updated, Unset) or _last_updated is None:
            last_updated = UNSET
        else:
            last_updated = isoparse(_last_updated)

        ou = d.pop("ou", UNSET)

        ou_id = d.pop("ouId", UNSET)

        ou_name = d.pop("ouName", UNSET)

        reimburse_tariff_id = d.pop("reimburseTariffId", UNSET)

        reimburse_tariff_name = d.pop("reimburseTariffName", UNSET)

        reimburse_tariff_price = d.pop("reimburseTariffPrice", UNSET)

        reimburse_tariff_calculated = d.pop("reimburseTariffCalculated", UNSET)

        _reimburse_price_calculated_on = d.pop("reimbursePriceCalculatedOn", UNSET)
        reimburse_price_calculated_on: datetime.datetime | Unset
        if isinstance(_reimburse_price_calculated_on, Unset) or _reimburse_price_calculated_on is None:
            reimburse_price_calculated_on = UNSET
        else:
            reimburse_price_calculated_on = isoparse(_reimburse_price_calculated_on)

        bank_account = d.pop("bankAccount", UNSET)

        _bank_account_created_on = d.pop("bankAccountCreatedOn", UNSET)
        bank_account_created_on: datetime.datetime | Unset
        if isinstance(_bank_account_created_on, Unset) or _bank_account_created_on is None:
            bank_account_created_on = UNSET
        else:
            bank_account_created_on = isoparse(_bank_account_created_on)

        _bank_account_valid_from = d.pop("bankAccountValidFrom", UNSET)
        bank_account_valid_from: datetime.datetime | Unset
        if isinstance(_bank_account_valid_from, Unset) or _bank_account_valid_from is None:
            bank_account_valid_from = UNSET
        else:
            bank_account_valid_from = isoparse(_bank_account_valid_from)

        reimburse_tariff_original_price = d.pop("reimburseTariffOriginalPrice", UNSET)

        has_guest_charging_reimbursement_fee = d.pop("hasGuestChargingReimbursementFee", UNSET)

        reimburse_tenant_fee = d.pop("reimburseTenantFee", UNSET)

        tenant_fee_calculated = d.pop("tenantFeeCalculated", UNSET)

        tariff_distribution_id = d.pop("tariffDistributionId", UNSET)

        _price_info = d.pop("priceInfo", UNSET)
        price_info: PriceInfoDto | Unset
        if isinstance(_price_info, Unset) or _price_info is None:
            price_info = UNSET
        else:
            price_info = PriceInfoDto.from_dict(_price_info)

        customer_share = d.pop("customerShare", UNSET)

        energy_compensation = d.pop("energyCompensation", UNSET)

        _reimbursement_customer_share = d.pop("reimbursementCustomerShare", UNSET)
        reimbursement_customer_share: ReimbursementCustomerShareDto | Unset
        if isinstance(_reimbursement_customer_share, Unset) or _reimbursement_customer_share is None:
            reimbursement_customer_share = UNSET
        else:
            reimbursement_customer_share = ReimbursementCustomerShareDto.from_dict(_reimbursement_customer_share)

        _local_start_date_time = d.pop("localStartDateTime", UNSET)
        local_start_date_time: datetime.datetime | Unset
        if isinstance(_local_start_date_time, Unset) or _local_start_date_time is None:
            local_start_date_time = UNSET
        else:
            local_start_date_time = isoparse(_local_start_date_time)

        _local_end_date_time = d.pop("localEndDateTime", UNSET)
        local_end_date_time: datetime.datetime | Unset
        if isinstance(_local_end_date_time, Unset) or _local_end_date_time is None:
            local_end_date_time = UNSET
        else:
            local_end_date_time = isoparse(_local_end_date_time)

        _ou_integration_info = d.pop("ouIntegrationInfo", UNSET)
        ou_integration_info: OuIntegrationInfoDto | Unset
        if isinstance(_ou_integration_info, Unset) or _ou_integration_info is None:
            ou_integration_info = UNSET
        else:
            ou_integration_info = OuIntegrationInfoDto.from_dict(_ou_integration_info)

        reimbursement_cdr_dto = cls(
            id=id,
            tenant_id=tenant_id,
            charge_point_id=charge_point_id,
            connector_id=connector_id,
            location_id=location_id,
            evse_id=evse_id,
            location=location,
            start_datetime=start_datetime,
            end_date_time=end_date_time,
            session_id=session_id,
            started_by_info=started_by_info,
            meter_start_in_wh=meter_start_in_wh,
            meter_stop_in_wh=meter_stop_in_wh,
            total_energy_in_kwh=total_energy_in_kwh,
            total_time_in_hours=total_time_in_hours,
            total_price=total_price,
            created=created,
            last_updated=last_updated,
            ou=ou,
            ou_id=ou_id,
            ou_name=ou_name,
            reimburse_tariff_id=reimburse_tariff_id,
            reimburse_tariff_name=reimburse_tariff_name,
            reimburse_tariff_price=reimburse_tariff_price,
            reimburse_tariff_calculated=reimburse_tariff_calculated,
            reimburse_price_calculated_on=reimburse_price_calculated_on,
            bank_account=bank_account,
            bank_account_created_on=bank_account_created_on,
            bank_account_valid_from=bank_account_valid_from,
            reimburse_tariff_original_price=reimburse_tariff_original_price,
            has_guest_charging_reimbursement_fee=has_guest_charging_reimbursement_fee,
            reimburse_tenant_fee=reimburse_tenant_fee,
            tenant_fee_calculated=tenant_fee_calculated,
            tariff_distribution_id=tariff_distribution_id,
            price_info=price_info,
            customer_share=customer_share,
            energy_compensation=energy_compensation,
            reimbursement_customer_share=reimbursement_customer_share,
            local_start_date_time=local_start_date_time,
            local_end_date_time=local_end_date_time,
            ou_integration_info=ou_integration_info,
        )

        reimbursement_cdr_dto.additional_properties = d
        return reimbursement_cdr_dto

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

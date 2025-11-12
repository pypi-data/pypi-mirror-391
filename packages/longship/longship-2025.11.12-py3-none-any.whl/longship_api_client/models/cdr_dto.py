from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.cdr_dto_approval_status import CdrDtoApprovalStatus
from ..models.cdr_dto_financial_type import CdrDtoFinancialType
from ..models.cdr_dto_reimbursement_type import CdrDtoReimbursementType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cdr_location_dto import CdrLocationDto
    from ..models.cdr_started_by_info_dto import CdrStartedByInfoDto
    from ..models.charging_period_dto import ChargingPeriodDto
    from ..models.price_info_dto import PriceInfoDto


T = TypeVar("T", bound="CdrDto")


@_attrs_define
class CdrDto:
    """
    Attributes:
        id (str | Unset):
        tenant_id (str | Unset):
        charge_point_id (str | Unset):
        connector_id (int | Unset):
        cdr_location (CdrLocationDto | Unset):
        start_datetime (datetime.datetime | Unset):
        end_date_time (datetime.datetime | Unset):
        session_id (str | Unset):
        token (str | Unset):
        started_by_info (CdrStartedByInfoDto | Unset):
        total_energy_in_kwh (float | Unset):
        total_time_in_hours (float | Unset):
        charging_periods (list[ChargingPeriodDto] | Unset):
        total_price (float | Unset):
        created (datetime.datetime | Unset):
        last_updated (datetime.datetime | Unset):
        ou (str | Unset):
        ou_id (str | Unset):
        ou_name (str | Unset):
        tariff_id (str | Unset):
        tariff_name (str | Unset):
        start_tariff (float | Unset):
        tariff_price (float | Unset):
        charging_time_tariff (float | Unset):
        parking_time_tariff (float | Unset):
        price_info (PriceInfoDto | Unset):
        local_start_date_time (datetime.datetime | Unset):
        local_end_date_time (datetime.datetime | Unset):
        approval_status (CdrDtoApprovalStatus | Unset):  Default: CdrDtoApprovalStatus.APPROVED.
        financial_type (CdrDtoFinancialType | Unset):  Default: CdrDtoFinancialType.DEBIT.
        debit_cdr_id (str | Unset):
        reimbursement_type (CdrDtoReimbursementType | Unset):  Default: CdrDtoReimbursementType.ORGANIZATIONUNIT.
    """

    id: str | Unset = UNSET
    tenant_id: str | Unset = UNSET
    charge_point_id: str | Unset = UNSET
    connector_id: int | Unset = UNSET
    cdr_location: CdrLocationDto | Unset = UNSET
    start_datetime: datetime.datetime | Unset = UNSET
    end_date_time: datetime.datetime | Unset = UNSET
    session_id: str | Unset = UNSET
    token: str | Unset = UNSET
    started_by_info: CdrStartedByInfoDto | Unset = UNSET
    total_energy_in_kwh: float | Unset = UNSET
    total_time_in_hours: float | Unset = UNSET
    charging_periods: list[ChargingPeriodDto] | Unset = UNSET
    total_price: float | Unset = UNSET
    created: datetime.datetime | Unset = UNSET
    last_updated: datetime.datetime | Unset = UNSET
    ou: str | Unset = UNSET
    ou_id: str | Unset = UNSET
    ou_name: str | Unset = UNSET
    tariff_id: str | Unset = UNSET
    tariff_name: str | Unset = UNSET
    start_tariff: float | Unset = UNSET
    tariff_price: float | Unset = UNSET
    charging_time_tariff: float | Unset = UNSET
    parking_time_tariff: float | Unset = UNSET
    price_info: PriceInfoDto | Unset = UNSET
    local_start_date_time: datetime.datetime | Unset = UNSET
    local_end_date_time: datetime.datetime | Unset = UNSET
    approval_status: CdrDtoApprovalStatus | Unset = CdrDtoApprovalStatus.APPROVED
    financial_type: CdrDtoFinancialType | Unset = CdrDtoFinancialType.DEBIT
    debit_cdr_id: str | Unset = UNSET
    reimbursement_type: CdrDtoReimbursementType | Unset = CdrDtoReimbursementType.ORGANIZATIONUNIT
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        tenant_id = self.tenant_id

        charge_point_id = self.charge_point_id

        connector_id = self.connector_id

        cdr_location: dict[str, Any] | Unset = UNSET
        if not isinstance(self.cdr_location, Unset):
            cdr_location = self.cdr_location.to_dict()

        start_datetime: str | Unset = UNSET
        if not isinstance(self.start_datetime, Unset):
            start_datetime = self.start_datetime.isoformat()

        end_date_time: str | Unset = UNSET
        if not isinstance(self.end_date_time, Unset):
            end_date_time = self.end_date_time.isoformat()

        session_id = self.session_id

        token = self.token

        started_by_info: dict[str, Any] | Unset = UNSET
        if not isinstance(self.started_by_info, Unset):
            started_by_info = self.started_by_info.to_dict()

        total_energy_in_kwh = self.total_energy_in_kwh

        total_time_in_hours = self.total_time_in_hours

        charging_periods: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.charging_periods, Unset):
            charging_periods = []
            for charging_periods_item_data in self.charging_periods:
                charging_periods_item = charging_periods_item_data.to_dict()
                charging_periods.append(charging_periods_item)

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

        tariff_id = self.tariff_id

        tariff_name = self.tariff_name

        start_tariff = self.start_tariff

        tariff_price = self.tariff_price

        charging_time_tariff = self.charging_time_tariff

        parking_time_tariff = self.parking_time_tariff

        price_info: dict[str, Any] | Unset = UNSET
        if not isinstance(self.price_info, Unset):
            price_info = self.price_info.to_dict()

        local_start_date_time: str | Unset = UNSET
        if not isinstance(self.local_start_date_time, Unset):
            local_start_date_time = self.local_start_date_time.isoformat()

        local_end_date_time: str | Unset = UNSET
        if not isinstance(self.local_end_date_time, Unset):
            local_end_date_time = self.local_end_date_time.isoformat()

        approval_status: str | Unset = UNSET
        if not isinstance(self.approval_status, Unset):
            approval_status = self.approval_status.value

        financial_type: str | Unset = UNSET
        if not isinstance(self.financial_type, Unset):
            financial_type = self.financial_type.value

        debit_cdr_id = self.debit_cdr_id

        reimbursement_type: str | Unset = UNSET
        if not isinstance(self.reimbursement_type, Unset):
            reimbursement_type = self.reimbursement_type.value

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
        if cdr_location is not UNSET:
            field_dict["cdrLocation"] = cdr_location
        if start_datetime is not UNSET:
            field_dict["startDatetime"] = start_datetime
        if end_date_time is not UNSET:
            field_dict["endDateTime"] = end_date_time
        if session_id is not UNSET:
            field_dict["sessionId"] = session_id
        if token is not UNSET:
            field_dict["token"] = token
        if started_by_info is not UNSET:
            field_dict["startedByInfo"] = started_by_info
        if total_energy_in_kwh is not UNSET:
            field_dict["totalEnergyInKwh"] = total_energy_in_kwh
        if total_time_in_hours is not UNSET:
            field_dict["totalTimeInHours"] = total_time_in_hours
        if charging_periods is not UNSET:
            field_dict["chargingPeriods"] = charging_periods
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
        if tariff_id is not UNSET:
            field_dict["tariffId"] = tariff_id
        if tariff_name is not UNSET:
            field_dict["tariffName"] = tariff_name
        if start_tariff is not UNSET:
            field_dict["startTariff"] = start_tariff
        if tariff_price is not UNSET:
            field_dict["tariffPrice"] = tariff_price
        if charging_time_tariff is not UNSET:
            field_dict["chargingTimeTariff"] = charging_time_tariff
        if parking_time_tariff is not UNSET:
            field_dict["parkingTimeTariff"] = parking_time_tariff
        if price_info is not UNSET:
            field_dict["priceInfo"] = price_info
        if local_start_date_time is not UNSET:
            field_dict["localStartDateTime"] = local_start_date_time
        if local_end_date_time is not UNSET:
            field_dict["localEndDateTime"] = local_end_date_time
        if approval_status is not UNSET:
            field_dict["approvalStatus"] = approval_status
        if financial_type is not UNSET:
            field_dict["financialType"] = financial_type
        if debit_cdr_id is not UNSET:
            field_dict["debitCdrId"] = debit_cdr_id
        if reimbursement_type is not UNSET:
            field_dict["reimbursementType"] = reimbursement_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cdr_location_dto import CdrLocationDto
        from ..models.cdr_started_by_info_dto import CdrStartedByInfoDto
        from ..models.charging_period_dto import ChargingPeriodDto
        from ..models.price_info_dto import PriceInfoDto

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        tenant_id = d.pop("tenantId", UNSET)

        charge_point_id = d.pop("chargePointId", UNSET)

        connector_id = d.pop("connectorId", UNSET)

        _cdr_location = d.pop("cdrLocation", UNSET)
        cdr_location: CdrLocationDto | Unset
        if isinstance(_cdr_location, Unset) or _cdr_location is None:
            cdr_location = UNSET
        else:
            cdr_location = CdrLocationDto.from_dict(_cdr_location)

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

        token = d.pop("token", UNSET)

        _started_by_info = d.pop("startedByInfo", UNSET)
        started_by_info: CdrStartedByInfoDto | Unset
        if isinstance(_started_by_info, Unset) or _started_by_info is None:
            started_by_info = UNSET
        else:
            started_by_info = CdrStartedByInfoDto.from_dict(_started_by_info)

        total_energy_in_kwh = d.pop("totalEnergyInKwh", UNSET)

        total_time_in_hours = d.pop("totalTimeInHours", UNSET)

        charging_periods = []
        _charging_periods = d.pop("chargingPeriods", UNSET)
        for charging_periods_item_data in _charging_periods or []:
            charging_periods_item = ChargingPeriodDto.from_dict(charging_periods_item_data)

            charging_periods.append(charging_periods_item)

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

        tariff_id = d.pop("tariffId", UNSET)

        tariff_name = d.pop("tariffName", UNSET)

        start_tariff = d.pop("startTariff", UNSET)

        tariff_price = d.pop("tariffPrice", UNSET)

        charging_time_tariff = d.pop("chargingTimeTariff", UNSET)

        parking_time_tariff = d.pop("parkingTimeTariff", UNSET)

        _price_info = d.pop("priceInfo", UNSET)
        price_info: PriceInfoDto | Unset
        if isinstance(_price_info, Unset) or _price_info is None:
            price_info = UNSET
        else:
            price_info = PriceInfoDto.from_dict(_price_info)

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

        _approval_status = d.pop("approvalStatus", UNSET)
        approval_status: CdrDtoApprovalStatus | Unset
        if isinstance(_approval_status, Unset) or _approval_status is None:
            approval_status = UNSET
        else:
            approval_status = CdrDtoApprovalStatus(_approval_status)

        _financial_type = d.pop("financialType", UNSET)
        financial_type: CdrDtoFinancialType | Unset
        if isinstance(_financial_type, Unset) or _financial_type is None:
            financial_type = UNSET
        else:
            financial_type = CdrDtoFinancialType(_financial_type)

        debit_cdr_id = d.pop("debitCdrId", UNSET)

        _reimbursement_type = d.pop("reimbursementType", UNSET)
        reimbursement_type: CdrDtoReimbursementType | Unset
        if isinstance(_reimbursement_type, Unset) or _reimbursement_type is None:
            reimbursement_type = UNSET
        else:
            reimbursement_type = CdrDtoReimbursementType(_reimbursement_type)

        cdr_dto = cls(
            id=id,
            tenant_id=tenant_id,
            charge_point_id=charge_point_id,
            connector_id=connector_id,
            cdr_location=cdr_location,
            start_datetime=start_datetime,
            end_date_time=end_date_time,
            session_id=session_id,
            token=token,
            started_by_info=started_by_info,
            total_energy_in_kwh=total_energy_in_kwh,
            total_time_in_hours=total_time_in_hours,
            charging_periods=charging_periods,
            total_price=total_price,
            created=created,
            last_updated=last_updated,
            ou=ou,
            ou_id=ou_id,
            ou_name=ou_name,
            tariff_id=tariff_id,
            tariff_name=tariff_name,
            start_tariff=start_tariff,
            tariff_price=tariff_price,
            charging_time_tariff=charging_time_tariff,
            parking_time_tariff=parking_time_tariff,
            price_info=price_info,
            local_start_date_time=local_start_date_time,
            local_end_date_time=local_end_date_time,
            approval_status=approval_status,
            financial_type=financial_type,
            debit_cdr_id=debit_cdr_id,
            reimbursement_type=reimbursement_type,
        )

        cdr_dto.additional_properties = d
        return cdr_dto

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

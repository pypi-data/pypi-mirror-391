from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.chargepoint_dto_connectivity_status import ChargepointDtoConnectivityStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.chargepoint_evse_dto import ChargepointEVSEDto


T = TypeVar("T", bound="ChargepointDto")


@_attrs_define
class ChargepointDto:
    """
    Attributes:
        id (str | Unset):
        charge_point_id (str | Unset):
        date_deleted (datetime.datetime | Unset):
        display_name (str | Unset):
        roaming_name (str | Unset):
        charge_box_serial_number (str | Unset):
        charge_point_model (str | Unset):
        charge_point_serial_number (str | Unset):
        charge_point_vendor (str | Unset):
        firmware_version (str | Unset):
        connectivity_status (ChargepointDtoConnectivityStatus | Unset):  Default:
            ChargepointDtoConnectivityStatus.ONLINE.
        iccid (str | Unset):
        imsi (str | Unset):
        meter_serial_number (str | Unset):
        meter_type (str | Unset):
        tenant_id (str | Unset):
        evses (list[ChargepointEVSEDto] | Unset):
        is_roaming (bool | Unset):
        has_guest_usage (bool | Unset):
        location_id (str | Unset):
        allow_any_token (bool | Unset):
        date_created (datetime.datetime | Unset):
        updated (datetime.datetime | Unset):
        ou (str | Unset):
        ou_id (str | Unset):
        ou_name (str | Unset):
        tariff_id (str | Unset):
        ad_hoc_tariff_id (str | Unset):
        tariff_name (str | Unset):
        ad_hoc_tariff_name (str | Unset):
        start_tariff (float | Unset):
        tariff_price (float | Unset):
        sim_card_number (str | Unset):
        token_groups (list[str] | Unset):
        is_new (bool | Unset):
        has_reimbursement (bool | Unset):
        reimburse_tariff_id (str | Unset):
        reimburse_tariff_name (str | Unset):
        reimburse_tariff_price (float | Unset):
        reimburse_uid (str | Unset):
        reimburse_token_id (str | Unset):
        reimburse_ou (str | Unset):
        use_tenant_fee (bool | Unset):
        max_capacity_in_kw (float | Unset):
        product_id (str | Unset):
        is_quarantined (bool | Unset):
        last_known_ocpp_version (str | Unset):
        websocket_disconnected (datetime.datetime | Unset):
    """

    id: str | Unset = UNSET
    charge_point_id: str | Unset = UNSET
    date_deleted: datetime.datetime | Unset = UNSET
    display_name: str | Unset = UNSET
    roaming_name: str | Unset = UNSET
    charge_box_serial_number: str | Unset = UNSET
    charge_point_model: str | Unset = UNSET
    charge_point_serial_number: str | Unset = UNSET
    charge_point_vendor: str | Unset = UNSET
    firmware_version: str | Unset = UNSET
    connectivity_status: ChargepointDtoConnectivityStatus | Unset = ChargepointDtoConnectivityStatus.ONLINE
    iccid: str | Unset = UNSET
    imsi: str | Unset = UNSET
    meter_serial_number: str | Unset = UNSET
    meter_type: str | Unset = UNSET
    tenant_id: str | Unset = UNSET
    evses: list[ChargepointEVSEDto] | Unset = UNSET
    is_roaming: bool | Unset = UNSET
    has_guest_usage: bool | Unset = UNSET
    location_id: str | Unset = UNSET
    allow_any_token: bool | Unset = UNSET
    date_created: datetime.datetime | Unset = UNSET
    updated: datetime.datetime | Unset = UNSET
    ou: str | Unset = UNSET
    ou_id: str | Unset = UNSET
    ou_name: str | Unset = UNSET
    tariff_id: str | Unset = UNSET
    ad_hoc_tariff_id: str | Unset = UNSET
    tariff_name: str | Unset = UNSET
    ad_hoc_tariff_name: str | Unset = UNSET
    start_tariff: float | Unset = UNSET
    tariff_price: float | Unset = UNSET
    sim_card_number: str | Unset = UNSET
    token_groups: list[str] | Unset = UNSET
    is_new: bool | Unset = UNSET
    has_reimbursement: bool | Unset = UNSET
    reimburse_tariff_id: str | Unset = UNSET
    reimburse_tariff_name: str | Unset = UNSET
    reimburse_tariff_price: float | Unset = UNSET
    reimburse_uid: str | Unset = UNSET
    reimburse_token_id: str | Unset = UNSET
    reimburse_ou: str | Unset = UNSET
    use_tenant_fee: bool | Unset = UNSET
    max_capacity_in_kw: float | Unset = UNSET
    product_id: str | Unset = UNSET
    is_quarantined: bool | Unset = UNSET
    last_known_ocpp_version: str | Unset = UNSET
    websocket_disconnected: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        charge_point_id = self.charge_point_id

        date_deleted: str | Unset = UNSET
        if not isinstance(self.date_deleted, Unset):
            date_deleted = self.date_deleted.isoformat()

        display_name = self.display_name

        roaming_name = self.roaming_name

        charge_box_serial_number = self.charge_box_serial_number

        charge_point_model = self.charge_point_model

        charge_point_serial_number = self.charge_point_serial_number

        charge_point_vendor = self.charge_point_vendor

        firmware_version = self.firmware_version

        connectivity_status: str | Unset = UNSET
        if not isinstance(self.connectivity_status, Unset):
            connectivity_status = self.connectivity_status.value

        iccid = self.iccid

        imsi = self.imsi

        meter_serial_number = self.meter_serial_number

        meter_type = self.meter_type

        tenant_id = self.tenant_id

        evses: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.evses, Unset):
            evses = []
            for evses_item_data in self.evses:
                evses_item = evses_item_data.to_dict()
                evses.append(evses_item)

        is_roaming = self.is_roaming

        has_guest_usage = self.has_guest_usage

        location_id = self.location_id

        allow_any_token = self.allow_any_token

        date_created: str | Unset = UNSET
        if not isinstance(self.date_created, Unset):
            date_created = self.date_created.isoformat()

        updated: str | Unset = UNSET
        if not isinstance(self.updated, Unset):
            updated = self.updated.isoformat()

        ou = self.ou

        ou_id = self.ou_id

        ou_name = self.ou_name

        tariff_id = self.tariff_id

        ad_hoc_tariff_id = self.ad_hoc_tariff_id

        tariff_name = self.tariff_name

        ad_hoc_tariff_name = self.ad_hoc_tariff_name

        start_tariff = self.start_tariff

        tariff_price = self.tariff_price

        sim_card_number = self.sim_card_number

        token_groups: list[str] | Unset = UNSET
        if not isinstance(self.token_groups, Unset):
            token_groups = self.token_groups

        is_new = self.is_new

        has_reimbursement = self.has_reimbursement

        reimburse_tariff_id = self.reimburse_tariff_id

        reimburse_tariff_name = self.reimburse_tariff_name

        reimburse_tariff_price = self.reimburse_tariff_price

        reimburse_uid = self.reimburse_uid

        reimburse_token_id = self.reimburse_token_id

        reimburse_ou = self.reimburse_ou

        use_tenant_fee = self.use_tenant_fee

        max_capacity_in_kw = self.max_capacity_in_kw

        product_id = self.product_id

        is_quarantined = self.is_quarantined

        last_known_ocpp_version = self.last_known_ocpp_version

        websocket_disconnected: str | Unset = UNSET
        if not isinstance(self.websocket_disconnected, Unset):
            websocket_disconnected = self.websocket_disconnected.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if charge_point_id is not UNSET:
            field_dict["chargePointId"] = charge_point_id
        if date_deleted is not UNSET:
            field_dict["dateDeleted"] = date_deleted
        if display_name is not UNSET:
            field_dict["displayName"] = display_name
        if roaming_name is not UNSET:
            field_dict["roamingName"] = roaming_name
        if charge_box_serial_number is not UNSET:
            field_dict["chargeBoxSerialNumber"] = charge_box_serial_number
        if charge_point_model is not UNSET:
            field_dict["chargePointModel"] = charge_point_model
        if charge_point_serial_number is not UNSET:
            field_dict["chargePointSerialNumber"] = charge_point_serial_number
        if charge_point_vendor is not UNSET:
            field_dict["chargePointVendor"] = charge_point_vendor
        if firmware_version is not UNSET:
            field_dict["firmwareVersion"] = firmware_version
        if connectivity_status is not UNSET:
            field_dict["connectivityStatus"] = connectivity_status
        if iccid is not UNSET:
            field_dict["iccid"] = iccid
        if imsi is not UNSET:
            field_dict["imsi"] = imsi
        if meter_serial_number is not UNSET:
            field_dict["meterSerialNumber"] = meter_serial_number
        if meter_type is not UNSET:
            field_dict["meterType"] = meter_type
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if evses is not UNSET:
            field_dict["evses"] = evses
        if is_roaming is not UNSET:
            field_dict["isRoaming"] = is_roaming
        if has_guest_usage is not UNSET:
            field_dict["hasGuestUsage"] = has_guest_usage
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if allow_any_token is not UNSET:
            field_dict["allowAnyToken"] = allow_any_token
        if date_created is not UNSET:
            field_dict["dateCreated"] = date_created
        if updated is not UNSET:
            field_dict["updated"] = updated
        if ou is not UNSET:
            field_dict["ou"] = ou
        if ou_id is not UNSET:
            field_dict["ouId"] = ou_id
        if ou_name is not UNSET:
            field_dict["ouName"] = ou_name
        if tariff_id is not UNSET:
            field_dict["tariffId"] = tariff_id
        if ad_hoc_tariff_id is not UNSET:
            field_dict["adHocTariffId"] = ad_hoc_tariff_id
        if tariff_name is not UNSET:
            field_dict["tariffName"] = tariff_name
        if ad_hoc_tariff_name is not UNSET:
            field_dict["adHocTariffName"] = ad_hoc_tariff_name
        if start_tariff is not UNSET:
            field_dict["startTariff"] = start_tariff
        if tariff_price is not UNSET:
            field_dict["tariffPrice"] = tariff_price
        if sim_card_number is not UNSET:
            field_dict["simCardNumber"] = sim_card_number
        if token_groups is not UNSET:
            field_dict["tokenGroups"] = token_groups
        if is_new is not UNSET:
            field_dict["isNew"] = is_new
        if has_reimbursement is not UNSET:
            field_dict["hasReimbursement"] = has_reimbursement
        if reimburse_tariff_id is not UNSET:
            field_dict["reimburseTariffId"] = reimburse_tariff_id
        if reimburse_tariff_name is not UNSET:
            field_dict["reimburseTariffName"] = reimburse_tariff_name
        if reimburse_tariff_price is not UNSET:
            field_dict["reimburseTariffPrice"] = reimburse_tariff_price
        if reimburse_uid is not UNSET:
            field_dict["reimburseUID"] = reimburse_uid
        if reimburse_token_id is not UNSET:
            field_dict["reimburseTokenId"] = reimburse_token_id
        if reimburse_ou is not UNSET:
            field_dict["reimburseOU"] = reimburse_ou
        if use_tenant_fee is not UNSET:
            field_dict["useTenantFee"] = use_tenant_fee
        if max_capacity_in_kw is not UNSET:
            field_dict["maxCapacityInKw"] = max_capacity_in_kw
        if product_id is not UNSET:
            field_dict["productId"] = product_id
        if is_quarantined is not UNSET:
            field_dict["isQuarantined"] = is_quarantined
        if last_known_ocpp_version is not UNSET:
            field_dict["lastKnownOcppVersion"] = last_known_ocpp_version
        if websocket_disconnected is not UNSET:
            field_dict["websocketDisconnected"] = websocket_disconnected

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.chargepoint_evse_dto import ChargepointEVSEDto

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        charge_point_id = d.pop("chargePointId", UNSET)

        _date_deleted = d.pop("dateDeleted", UNSET)
        date_deleted: datetime.datetime | Unset
        if isinstance(_date_deleted, Unset) or _date_deleted is None:
            date_deleted = UNSET
        else:
            date_deleted = isoparse(_date_deleted)

        display_name = d.pop("displayName", UNSET)

        roaming_name = d.pop("roamingName", UNSET)

        charge_box_serial_number = d.pop("chargeBoxSerialNumber", UNSET)

        charge_point_model = d.pop("chargePointModel", UNSET)

        charge_point_serial_number = d.pop("chargePointSerialNumber", UNSET)

        charge_point_vendor = d.pop("chargePointVendor", UNSET)

        firmware_version = d.pop("firmwareVersion", UNSET)

        _connectivity_status = d.pop("connectivityStatus", UNSET)
        connectivity_status: ChargepointDtoConnectivityStatus | Unset
        if isinstance(_connectivity_status, Unset) or _connectivity_status is None:
            connectivity_status = UNSET
        else:
            connectivity_status = ChargepointDtoConnectivityStatus(_connectivity_status)

        iccid = d.pop("iccid", UNSET)

        imsi = d.pop("imsi", UNSET)

        meter_serial_number = d.pop("meterSerialNumber", UNSET)

        meter_type = d.pop("meterType", UNSET)

        tenant_id = d.pop("tenantId", UNSET)

        evses = []
        _evses = d.pop("evses", UNSET)
        for evses_item_data in _evses or []:
            evses_item = ChargepointEVSEDto.from_dict(evses_item_data)

            evses.append(evses_item)

        is_roaming = d.pop("isRoaming", UNSET)

        has_guest_usage = d.pop("hasGuestUsage", UNSET)

        location_id = d.pop("locationId", UNSET)

        allow_any_token = d.pop("allowAnyToken", UNSET)

        _date_created = d.pop("dateCreated", UNSET)
        date_created: datetime.datetime | Unset
        if isinstance(_date_created, Unset) or _date_created is None:
            date_created = UNSET
        else:
            date_created = isoparse(_date_created)

        _updated = d.pop("updated", UNSET)
        updated: datetime.datetime | Unset
        if isinstance(_updated, Unset) or _updated is None:
            updated = UNSET
        else:
            updated = isoparse(_updated)

        ou = d.pop("ou", UNSET)

        ou_id = d.pop("ouId", UNSET)

        ou_name = d.pop("ouName", UNSET)

        tariff_id = d.pop("tariffId", UNSET)

        ad_hoc_tariff_id = d.pop("adHocTariffId", UNSET)

        tariff_name = d.pop("tariffName", UNSET)

        ad_hoc_tariff_name = d.pop("adHocTariffName", UNSET)

        start_tariff = d.pop("startTariff", UNSET)

        tariff_price = d.pop("tariffPrice", UNSET)

        sim_card_number = d.pop("simCardNumber", UNSET)

        token_groups = cast(list[str], d.pop("tokenGroups", UNSET))

        is_new = d.pop("isNew", UNSET)

        has_reimbursement = d.pop("hasReimbursement", UNSET)

        reimburse_tariff_id = d.pop("reimburseTariffId", UNSET)

        reimburse_tariff_name = d.pop("reimburseTariffName", UNSET)

        reimburse_tariff_price = d.pop("reimburseTariffPrice", UNSET)

        reimburse_uid = d.pop("reimburseUID", UNSET)

        reimburse_token_id = d.pop("reimburseTokenId", UNSET)

        reimburse_ou = d.pop("reimburseOU", UNSET)

        use_tenant_fee = d.pop("useTenantFee", UNSET)

        max_capacity_in_kw = d.pop("maxCapacityInKw", UNSET)

        product_id = d.pop("productId", UNSET)

        is_quarantined = d.pop("isQuarantined", UNSET)

        last_known_ocpp_version = d.pop("lastKnownOcppVersion", UNSET)

        _websocket_disconnected = d.pop("websocketDisconnected", UNSET)
        websocket_disconnected: datetime.datetime | Unset
        if isinstance(_websocket_disconnected, Unset) or _websocket_disconnected is None:
            websocket_disconnected = UNSET
        else:
            websocket_disconnected = isoparse(_websocket_disconnected)

        chargepoint_dto = cls(
            id=id,
            charge_point_id=charge_point_id,
            date_deleted=date_deleted,
            display_name=display_name,
            roaming_name=roaming_name,
            charge_box_serial_number=charge_box_serial_number,
            charge_point_model=charge_point_model,
            charge_point_serial_number=charge_point_serial_number,
            charge_point_vendor=charge_point_vendor,
            firmware_version=firmware_version,
            connectivity_status=connectivity_status,
            iccid=iccid,
            imsi=imsi,
            meter_serial_number=meter_serial_number,
            meter_type=meter_type,
            tenant_id=tenant_id,
            evses=evses,
            is_roaming=is_roaming,
            has_guest_usage=has_guest_usage,
            location_id=location_id,
            allow_any_token=allow_any_token,
            date_created=date_created,
            updated=updated,
            ou=ou,
            ou_id=ou_id,
            ou_name=ou_name,
            tariff_id=tariff_id,
            ad_hoc_tariff_id=ad_hoc_tariff_id,
            tariff_name=tariff_name,
            ad_hoc_tariff_name=ad_hoc_tariff_name,
            start_tariff=start_tariff,
            tariff_price=tariff_price,
            sim_card_number=sim_card_number,
            token_groups=token_groups,
            is_new=is_new,
            has_reimbursement=has_reimbursement,
            reimburse_tariff_id=reimburse_tariff_id,
            reimburse_tariff_name=reimburse_tariff_name,
            reimburse_tariff_price=reimburse_tariff_price,
            reimburse_uid=reimburse_uid,
            reimburse_token_id=reimburse_token_id,
            reimburse_ou=reimburse_ou,
            use_tenant_fee=use_tenant_fee,
            max_capacity_in_kw=max_capacity_in_kw,
            product_id=product_id,
            is_quarantined=is_quarantined,
            last_known_ocpp_version=last_known_ocpp_version,
            websocket_disconnected=websocket_disconnected,
        )

        chargepoint_dto.additional_properties = d
        return chargepoint_dto

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

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.chargepoint_connector_dto_format import ChargepointConnectorDtoFormat
from ..models.chargepoint_connector_dto_operational_status import ChargepointConnectorDtoOperationalStatus
from ..models.chargepoint_connector_dto_power_type import ChargepointConnectorDtoPowerType
from ..models.chargepoint_connector_dto_standard import ChargepointConnectorDtoStandard
from ..types import UNSET, Unset

T = TypeVar("T", bound="ChargepointConnectorDto")


@_attrs_define
class ChargepointConnectorDto:
    """
    Attributes:
        id (str | Unset):
        operational_status (ChargepointConnectorDtoOperationalStatus | Unset):  Default:
            ChargepointConnectorDtoOperationalStatus.AVAILABLE.
        standard (ChargepointConnectorDtoStandard | Unset):  Default: ChargepointConnectorDtoStandard.CHADEMO.
        format_ (ChargepointConnectorDtoFormat | Unset):  Default: ChargepointConnectorDtoFormat.SOCKET.
        power_type (ChargepointConnectorDtoPowerType | Unset):  Default: ChargepointConnectorDtoPowerType.AC_1_PHASE.
        max_voltage (int | Unset):
        max_amperage (int | Unset):
        max_electric_power (int | Unset):
        tariff_id (str | Unset):
        ad_hoc_tariff_id (str | Unset):
    """

    id: str | Unset = UNSET
    operational_status: ChargepointConnectorDtoOperationalStatus | Unset = (
        ChargepointConnectorDtoOperationalStatus.AVAILABLE
    )
    standard: ChargepointConnectorDtoStandard | Unset = ChargepointConnectorDtoStandard.CHADEMO
    format_: ChargepointConnectorDtoFormat | Unset = ChargepointConnectorDtoFormat.SOCKET
    power_type: ChargepointConnectorDtoPowerType | Unset = ChargepointConnectorDtoPowerType.AC_1_PHASE
    max_voltage: int | Unset = UNSET
    max_amperage: int | Unset = UNSET
    max_electric_power: int | Unset = UNSET
    tariff_id: str | Unset = UNSET
    ad_hoc_tariff_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        operational_status: str | Unset = UNSET
        if not isinstance(self.operational_status, Unset):
            operational_status = self.operational_status.value

        standard: str | Unset = UNSET
        if not isinstance(self.standard, Unset):
            standard = self.standard.value

        format_: str | Unset = UNSET
        if not isinstance(self.format_, Unset):
            format_ = self.format_.value

        power_type: str | Unset = UNSET
        if not isinstance(self.power_type, Unset):
            power_type = self.power_type.value

        max_voltage = self.max_voltage

        max_amperage = self.max_amperage

        max_electric_power = self.max_electric_power

        tariff_id = self.tariff_id

        ad_hoc_tariff_id = self.ad_hoc_tariff_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if operational_status is not UNSET:
            field_dict["operationalStatus"] = operational_status
        if standard is not UNSET:
            field_dict["standard"] = standard
        if format_ is not UNSET:
            field_dict["format"] = format_
        if power_type is not UNSET:
            field_dict["powerType"] = power_type
        if max_voltage is not UNSET:
            field_dict["maxVoltage"] = max_voltage
        if max_amperage is not UNSET:
            field_dict["maxAmperage"] = max_amperage
        if max_electric_power is not UNSET:
            field_dict["maxElectricPower"] = max_electric_power
        if tariff_id is not UNSET:
            field_dict["tariffId"] = tariff_id
        if ad_hoc_tariff_id is not UNSET:
            field_dict["adHocTariffId"] = ad_hoc_tariff_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        _operational_status = d.pop("operationalStatus", UNSET)
        operational_status: ChargepointConnectorDtoOperationalStatus | Unset
        if isinstance(_operational_status, Unset) or _operational_status is None:
            operational_status = UNSET
        else:
            operational_status = ChargepointConnectorDtoOperationalStatus(_operational_status)

        _standard = d.pop("standard", UNSET)
        standard: ChargepointConnectorDtoStandard | Unset
        if isinstance(_standard, Unset) or _standard is None:
            standard = UNSET
        else:
            standard = ChargepointConnectorDtoStandard(_standard)

        _format_ = d.pop("format", UNSET)
        format_: ChargepointConnectorDtoFormat | Unset
        if isinstance(_format_, Unset) or _format_ is None:
            format_ = UNSET
        else:
            format_ = ChargepointConnectorDtoFormat(_format_)

        _power_type = d.pop("powerType", UNSET)
        power_type: ChargepointConnectorDtoPowerType | Unset
        if isinstance(_power_type, Unset) or _power_type is None:
            power_type = UNSET
        else:
            power_type = ChargepointConnectorDtoPowerType(_power_type)

        max_voltage = d.pop("maxVoltage", UNSET)

        max_amperage = d.pop("maxAmperage", UNSET)

        max_electric_power = d.pop("maxElectricPower", UNSET)

        tariff_id = d.pop("tariffId", UNSET)

        ad_hoc_tariff_id = d.pop("adHocTariffId", UNSET)

        chargepoint_connector_dto = cls(
            id=id,
            operational_status=operational_status,
            standard=standard,
            format_=format_,
            power_type=power_type,
            max_voltage=max_voltage,
            max_amperage=max_amperage,
            max_electric_power=max_electric_power,
            tariff_id=tariff_id,
            ad_hoc_tariff_id=ad_hoc_tariff_id,
        )

        chargepoint_connector_dto.additional_properties = d
        return chargepoint_connector_dto

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

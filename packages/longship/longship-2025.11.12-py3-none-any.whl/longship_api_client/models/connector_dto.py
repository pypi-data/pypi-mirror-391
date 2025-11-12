from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.connector_dto_format import ConnectorDtoFormat
from ..models.connector_dto_power_type import ConnectorDtoPowerType
from ..models.connector_dto_standard import ConnectorDtoStandard
from ..types import UNSET, Unset

T = TypeVar("T", bound="ConnectorDto")


@_attrs_define
class ConnectorDto:
    """
    Attributes:
        id (str | Unset):
        standard (ConnectorDtoStandard | Unset):  Default: ConnectorDtoStandard.CHADEMO.
        format_ (ConnectorDtoFormat | Unset):  Default: ConnectorDtoFormat.SOCKET.
        power_type (ConnectorDtoPowerType | Unset):  Default: ConnectorDtoPowerType.AC_1_PHASE.
        max_voltage (int | Unset):
        max_amperage (int | Unset):
        max_electric_power (int | Unset):
        calc_max_electric_power (bool | Unset):
        terms_and_conditions (str | Unset):
        last_updated (datetime.datetime | Unset):
    """

    id: str | Unset = UNSET
    standard: ConnectorDtoStandard | Unset = ConnectorDtoStandard.CHADEMO
    format_: ConnectorDtoFormat | Unset = ConnectorDtoFormat.SOCKET
    power_type: ConnectorDtoPowerType | Unset = ConnectorDtoPowerType.AC_1_PHASE
    max_voltage: int | Unset = UNSET
    max_amperage: int | Unset = UNSET
    max_electric_power: int | Unset = UNSET
    calc_max_electric_power: bool | Unset = UNSET
    terms_and_conditions: str | Unset = UNSET
    last_updated: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

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

        calc_max_electric_power = self.calc_max_electric_power

        terms_and_conditions = self.terms_and_conditions

        last_updated: str | Unset = UNSET
        if not isinstance(self.last_updated, Unset):
            last_updated = self.last_updated.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if standard is not UNSET:
            field_dict["standard"] = standard
        if format_ is not UNSET:
            field_dict["format"] = format_
        if power_type is not UNSET:
            field_dict["power_type"] = power_type
        if max_voltage is not UNSET:
            field_dict["max_voltage"] = max_voltage
        if max_amperage is not UNSET:
            field_dict["max_amperage"] = max_amperage
        if max_electric_power is not UNSET:
            field_dict["max_electric_power"] = max_electric_power
        if calc_max_electric_power is not UNSET:
            field_dict["calc_max_electric_power"] = calc_max_electric_power
        if terms_and_conditions is not UNSET:
            field_dict["terms_and_conditions"] = terms_and_conditions
        if last_updated is not UNSET:
            field_dict["last_updated"] = last_updated

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        _standard = d.pop("standard", UNSET)
        standard: ConnectorDtoStandard | Unset
        if isinstance(_standard, Unset) or _standard is None:
            standard = UNSET
        else:
            standard = ConnectorDtoStandard(_standard)

        _format_ = d.pop("format", UNSET)
        format_: ConnectorDtoFormat | Unset
        if isinstance(_format_, Unset) or _format_ is None:
            format_ = UNSET
        else:
            format_ = ConnectorDtoFormat(_format_)

        _power_type = d.pop("power_type", UNSET)
        power_type: ConnectorDtoPowerType | Unset
        if isinstance(_power_type, Unset) or _power_type is None:
            power_type = UNSET
        else:
            power_type = ConnectorDtoPowerType(_power_type)

        max_voltage = d.pop("max_voltage", UNSET)

        max_amperage = d.pop("max_amperage", UNSET)

        max_electric_power = d.pop("max_electric_power", UNSET)

        calc_max_electric_power = d.pop("calc_max_electric_power", UNSET)

        terms_and_conditions = d.pop("terms_and_conditions", UNSET)

        _last_updated = d.pop("last_updated", UNSET)
        last_updated: datetime.datetime | Unset
        if isinstance(_last_updated, Unset) or _last_updated is None:
            last_updated = UNSET
        else:
            last_updated = isoparse(_last_updated)

        connector_dto = cls(
            id=id,
            standard=standard,
            format_=format_,
            power_type=power_type,
            max_voltage=max_voltage,
            max_amperage=max_amperage,
            max_electric_power=max_electric_power,
            calc_max_electric_power=calc_max_electric_power,
            terms_and_conditions=terms_and_conditions,
            last_updated=last_updated,
        )

        connector_dto.additional_properties = d
        return connector_dto

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

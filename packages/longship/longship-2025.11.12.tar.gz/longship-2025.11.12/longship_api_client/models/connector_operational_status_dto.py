from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.connector_operational_status_dto_operational_status import ConnectorOperationalStatusDtoOperationalStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="ConnectorOperationalStatusDto")


@_attrs_define
class ConnectorOperationalStatusDto:
    """
    Attributes:
        connector_number (int | Unset):
        evse_number (int | Unset):
        operational_status (ConnectorOperationalStatusDtoOperationalStatus | Unset):  Default:
            ConnectorOperationalStatusDtoOperationalStatus.AVAILABLE.
        timestamp (datetime.datetime | Unset):
    """

    connector_number: int | Unset = UNSET
    evse_number: int | Unset = UNSET
    operational_status: ConnectorOperationalStatusDtoOperationalStatus | Unset = (
        ConnectorOperationalStatusDtoOperationalStatus.AVAILABLE
    )
    timestamp: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        connector_number = self.connector_number

        evse_number = self.evse_number

        operational_status: str | Unset = UNSET
        if not isinstance(self.operational_status, Unset):
            operational_status = self.operational_status.value

        timestamp: str | Unset = UNSET
        if not isinstance(self.timestamp, Unset):
            timestamp = self.timestamp.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if connector_number is not UNSET:
            field_dict["connectorNumber"] = connector_number
        if evse_number is not UNSET:
            field_dict["evseNumber"] = evse_number
        if operational_status is not UNSET:
            field_dict["operationalStatus"] = operational_status
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        connector_number = d.pop("connectorNumber", UNSET)

        evse_number = d.pop("evseNumber", UNSET)

        _operational_status = d.pop("operationalStatus", UNSET)
        operational_status: ConnectorOperationalStatusDtoOperationalStatus | Unset
        if isinstance(_operational_status, Unset) or _operational_status is None:
            operational_status = UNSET
        else:
            operational_status = ConnectorOperationalStatusDtoOperationalStatus(_operational_status)

        _timestamp = d.pop("timestamp", UNSET)
        timestamp: datetime.datetime | Unset
        if isinstance(_timestamp, Unset) or _timestamp is None:
            timestamp = UNSET
        else:
            timestamp = isoparse(_timestamp)

        connector_operational_status_dto = cls(
            connector_number=connector_number,
            evse_number=evse_number,
            operational_status=operational_status,
            timestamp=timestamp,
        )

        connector_operational_status_dto.additional_properties = d
        return connector_operational_status_dto

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

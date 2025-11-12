from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.chargepoint_status_dto_connectivity_status import ChargepointStatusDtoConnectivityStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.connector_operational_status_dto import ConnectorOperationalStatusDto


T = TypeVar("T", bound="ChargepointStatusDto")


@_attrs_define
class ChargepointStatusDto:
    """
    Attributes:
        id (str | Unset):
        display_name (str | Unset):
        tenant_id (str | Unset):
        ou (str | Unset):
        ou_id (str | Unset):
        ou_name (str | Unset):
        timestamp (datetime.datetime | Unset):
        connectivity_status (ChargepointStatusDtoConnectivityStatus | Unset):  Default:
            ChargepointStatusDtoConnectivityStatus.ONLINE.
        connectors (list[ConnectorOperationalStatusDto] | Unset):
        websocket_connected (datetime.datetime | Unset):
        websocket_disconnected (datetime.datetime | Unset):
    """

    id: str | Unset = UNSET
    display_name: str | Unset = UNSET
    tenant_id: str | Unset = UNSET
    ou: str | Unset = UNSET
    ou_id: str | Unset = UNSET
    ou_name: str | Unset = UNSET
    timestamp: datetime.datetime | Unset = UNSET
    connectivity_status: ChargepointStatusDtoConnectivityStatus | Unset = ChargepointStatusDtoConnectivityStatus.ONLINE
    connectors: list[ConnectorOperationalStatusDto] | Unset = UNSET
    websocket_connected: datetime.datetime | Unset = UNSET
    websocket_disconnected: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        display_name = self.display_name

        tenant_id = self.tenant_id

        ou = self.ou

        ou_id = self.ou_id

        ou_name = self.ou_name

        timestamp: str | Unset = UNSET
        if not isinstance(self.timestamp, Unset):
            timestamp = self.timestamp.isoformat()

        connectivity_status: str | Unset = UNSET
        if not isinstance(self.connectivity_status, Unset):
            connectivity_status = self.connectivity_status.value

        connectors: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.connectors, Unset):
            connectors = []
            for connectors_item_data in self.connectors:
                connectors_item = connectors_item_data.to_dict()
                connectors.append(connectors_item)

        websocket_connected: str | Unset = UNSET
        if not isinstance(self.websocket_connected, Unset):
            websocket_connected = self.websocket_connected.isoformat()

        websocket_disconnected: str | Unset = UNSET
        if not isinstance(self.websocket_disconnected, Unset):
            websocket_disconnected = self.websocket_disconnected.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if display_name is not UNSET:
            field_dict["displayName"] = display_name
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if ou is not UNSET:
            field_dict["ou"] = ou
        if ou_id is not UNSET:
            field_dict["ouId"] = ou_id
        if ou_name is not UNSET:
            field_dict["ouName"] = ou_name
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp
        if connectivity_status is not UNSET:
            field_dict["connectivityStatus"] = connectivity_status
        if connectors is not UNSET:
            field_dict["connectors"] = connectors
        if websocket_connected is not UNSET:
            field_dict["websocketConnected"] = websocket_connected
        if websocket_disconnected is not UNSET:
            field_dict["websocketDisconnected"] = websocket_disconnected

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.connector_operational_status_dto import ConnectorOperationalStatusDto

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        display_name = d.pop("displayName", UNSET)

        tenant_id = d.pop("tenantId", UNSET)

        ou = d.pop("ou", UNSET)

        ou_id = d.pop("ouId", UNSET)

        ou_name = d.pop("ouName", UNSET)

        _timestamp = d.pop("timestamp", UNSET)
        timestamp: datetime.datetime | Unset
        if isinstance(_timestamp, Unset) or _timestamp is None:
            timestamp = UNSET
        else:
            timestamp = isoparse(_timestamp)

        _connectivity_status = d.pop("connectivityStatus", UNSET)
        connectivity_status: ChargepointStatusDtoConnectivityStatus | Unset
        if isinstance(_connectivity_status, Unset) or _connectivity_status is None:
            connectivity_status = UNSET
        else:
            connectivity_status = ChargepointStatusDtoConnectivityStatus(_connectivity_status)

        connectors = []
        _connectors = d.pop("connectors", UNSET)
        for connectors_item_data in _connectors or []:
            connectors_item = ConnectorOperationalStatusDto.from_dict(connectors_item_data)

            connectors.append(connectors_item)

        _websocket_connected = d.pop("websocketConnected", UNSET)
        websocket_connected: datetime.datetime | Unset
        if isinstance(_websocket_connected, Unset) or _websocket_connected is None:
            websocket_connected = UNSET
        else:
            websocket_connected = isoparse(_websocket_connected)

        _websocket_disconnected = d.pop("websocketDisconnected", UNSET)
        websocket_disconnected: datetime.datetime | Unset
        if isinstance(_websocket_disconnected, Unset) or _websocket_disconnected is None:
            websocket_disconnected = UNSET
        else:
            websocket_disconnected = isoparse(_websocket_disconnected)

        chargepoint_status_dto = cls(
            id=id,
            display_name=display_name,
            tenant_id=tenant_id,
            ou=ou,
            ou_id=ou_id,
            ou_name=ou_name,
            timestamp=timestamp,
            connectivity_status=connectivity_status,
            connectors=connectors,
            websocket_connected=websocket_connected,
            websocket_disconnected=websocket_disconnected,
        )

        chargepoint_status_dto.additional_properties = d
        return chargepoint_status_dto

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

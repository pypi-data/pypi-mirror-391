from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.message_log_dto_direction import MessageLogDtoDirection
from ..models.message_log_dto_ocpp_message_type import MessageLogDtoOcppMessageType
from ..models.message_log_dto_wamp_message_type import MessageLogDtoWampMessageType
from ..types import UNSET, Unset

T = TypeVar("T", bound="MessageLogDto")


@_attrs_define
class MessageLogDto:
    """
    Attributes:
        id (str | Unset):
        charge_point_id (str | Unset):
        message_id (str | Unset):
        wamp_message_type (MessageLogDtoWampMessageType | Unset):  Default: MessageLogDtoWampMessageType.UNKNOWN.
        ocpp_message_type (MessageLogDtoOcppMessageType | Unset):  Default: MessageLogDtoOcppMessageType.AUTHORIZE.
        direction (MessageLogDtoDirection | Unset):  Default: MessageLogDtoDirection.UNKNOWN.
        tenant_id (str | Unset):
        payload (str | Unset):
        timestamp (datetime.datetime | Unset):
    """

    id: str | Unset = UNSET
    charge_point_id: str | Unset = UNSET
    message_id: str | Unset = UNSET
    wamp_message_type: MessageLogDtoWampMessageType | Unset = MessageLogDtoWampMessageType.UNKNOWN
    ocpp_message_type: MessageLogDtoOcppMessageType | Unset = MessageLogDtoOcppMessageType.AUTHORIZE
    direction: MessageLogDtoDirection | Unset = MessageLogDtoDirection.UNKNOWN
    tenant_id: str | Unset = UNSET
    payload: str | Unset = UNSET
    timestamp: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        charge_point_id = self.charge_point_id

        message_id = self.message_id

        wamp_message_type: str | Unset = UNSET
        if not isinstance(self.wamp_message_type, Unset):
            wamp_message_type = self.wamp_message_type.value

        ocpp_message_type: str | Unset = UNSET
        if not isinstance(self.ocpp_message_type, Unset):
            ocpp_message_type = self.ocpp_message_type.value

        direction: str | Unset = UNSET
        if not isinstance(self.direction, Unset):
            direction = self.direction.value

        tenant_id = self.tenant_id

        payload = self.payload

        timestamp: str | Unset = UNSET
        if not isinstance(self.timestamp, Unset):
            timestamp = self.timestamp.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if charge_point_id is not UNSET:
            field_dict["chargePointId"] = charge_point_id
        if message_id is not UNSET:
            field_dict["messageId"] = message_id
        if wamp_message_type is not UNSET:
            field_dict["wampMessageType"] = wamp_message_type
        if ocpp_message_type is not UNSET:
            field_dict["ocppMessageType"] = ocpp_message_type
        if direction is not UNSET:
            field_dict["direction"] = direction
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if payload is not UNSET:
            field_dict["payload"] = payload
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        charge_point_id = d.pop("chargePointId", UNSET)

        message_id = d.pop("messageId", UNSET)

        _wamp_message_type = d.pop("wampMessageType", UNSET)
        wamp_message_type: MessageLogDtoWampMessageType | Unset
        if isinstance(_wamp_message_type, Unset) or _wamp_message_type is None:
            wamp_message_type = UNSET
        else:
            wamp_message_type = MessageLogDtoWampMessageType(_wamp_message_type)

        _ocpp_message_type = d.pop("ocppMessageType", UNSET)
        ocpp_message_type: MessageLogDtoOcppMessageType | Unset
        if isinstance(_ocpp_message_type, Unset) or _ocpp_message_type is None:
            ocpp_message_type = UNSET
        else:
            ocpp_message_type = MessageLogDtoOcppMessageType(_ocpp_message_type)

        _direction = d.pop("direction", UNSET)
        direction: MessageLogDtoDirection | Unset
        if isinstance(_direction, Unset) or _direction is None:
            direction = UNSET
        else:
            direction = MessageLogDtoDirection(_direction)

        tenant_id = d.pop("tenantId", UNSET)

        payload = d.pop("payload", UNSET)

        _timestamp = d.pop("timestamp", UNSET)
        timestamp: datetime.datetime | Unset
        if isinstance(_timestamp, Unset) or _timestamp is None:
            timestamp = UNSET
        else:
            timestamp = isoparse(_timestamp)

        message_log_dto = cls(
            id=id,
            charge_point_id=charge_point_id,
            message_id=message_id,
            wamp_message_type=wamp_message_type,
            ocpp_message_type=ocpp_message_type,
            direction=direction,
            tenant_id=tenant_id,
            payload=payload,
            timestamp=timestamp,
        )

        message_log_dto.additional_properties = d
        return message_log_dto

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

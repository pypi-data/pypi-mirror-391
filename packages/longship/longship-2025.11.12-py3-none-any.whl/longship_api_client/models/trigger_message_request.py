from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.trigger_message_request_requested_message import TriggerMessageRequestRequestedMessage
from ..types import UNSET, Unset

T = TypeVar("T", bound="TriggerMessageRequest")


@_attrs_define
class TriggerMessageRequest:
    """
    Attributes:
        requested_message (TriggerMessageRequestRequestedMessage):  Default:
            TriggerMessageRequestRequestedMessage.BOOTNOTIFICATION.
        connector_id (int | Unset):
    """

    requested_message: TriggerMessageRequestRequestedMessage = TriggerMessageRequestRequestedMessage.BOOTNOTIFICATION
    connector_id: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        requested_message = self.requested_message.value

        connector_id = self.connector_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "requestedMessage": requested_message,
            }
        )
        if connector_id is not UNSET:
            field_dict["connectorId"] = connector_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        requested_message = TriggerMessageRequestRequestedMessage(d.pop("requestedMessage"))

        connector_id = d.pop("connectorId", UNSET)

        trigger_message_request = cls(
            requested_message=requested_message,
            connector_id=connector_id,
        )

        trigger_message_request.additional_properties = d
        return trigger_message_request

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

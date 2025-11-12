from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.change_availability_request_type import ChangeAvailabilityRequestType

T = TypeVar("T", bound="ChangeAvailabilityRequest")


@_attrs_define
class ChangeAvailabilityRequest:
    """
    Attributes:
        connector_id (int):
        type_ (ChangeAvailabilityRequestType):  Default: ChangeAvailabilityRequestType.INOPERATIVE.
    """

    connector_id: int
    type_: ChangeAvailabilityRequestType = ChangeAvailabilityRequestType.INOPERATIVE
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        connector_id = self.connector_id

        type_ = self.type_.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "connectorId": connector_id,
                "type": type_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        connector_id = d.pop("connectorId")

        type_ = ChangeAvailabilityRequestType(d.pop("type"))

        change_availability_request = cls(
            connector_id=connector_id,
            type_=type_,
        )

        change_availability_request.additional_properties = d
        return change_availability_request

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

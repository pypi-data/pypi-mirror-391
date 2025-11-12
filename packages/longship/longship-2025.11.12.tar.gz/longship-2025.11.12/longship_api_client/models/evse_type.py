from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.custom_data_type import CustomDataType


T = TypeVar("T", bound="EvseType")


@_attrs_define
class EvseType:
    """
    Attributes:
        id (int):
        custom_data (CustomDataType | Unset):
        connector_id (int | Unset):
    """

    id: int
    custom_data: CustomDataType | Unset = UNSET
    connector_id: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        custom_data: dict[str, Any] | Unset = UNSET
        if not isinstance(self.custom_data, Unset):
            custom_data = self.custom_data.to_dict()

        connector_id = self.connector_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if custom_data is not UNSET:
            field_dict["customData"] = custom_data
        if connector_id is not UNSET:
            field_dict["connectorId"] = connector_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.custom_data_type import CustomDataType

        d = dict(src_dict)
        id = d.pop("id")

        _custom_data = d.pop("customData", UNSET)
        custom_data: CustomDataType | Unset
        if isinstance(_custom_data, Unset) or _custom_data is None:
            custom_data = UNSET
        else:
            custom_data = CustomDataType.from_dict(_custom_data)

        connector_id = d.pop("connectorId", UNSET)

        evse_type = cls(
            id=id,
            custom_data=custom_data,
            connector_id=connector_id,
        )

        evse_type.additional_properties = d
        return evse_type

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

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.custom_data_type import CustomDataType
    from ..models.evse_type import EvseType


T = TypeVar("T", bound="ComponentType")


@_attrs_define
class ComponentType:
    """
    Attributes:
        name (str):
        custom_data (CustomDataType | Unset):
        evse (EvseType | Unset):
        instance (str | Unset):
    """

    name: str
    custom_data: CustomDataType | Unset = UNSET
    evse: EvseType | Unset = UNSET
    instance: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        custom_data: dict[str, Any] | Unset = UNSET
        if not isinstance(self.custom_data, Unset):
            custom_data = self.custom_data.to_dict()

        evse: dict[str, Any] | Unset = UNSET
        if not isinstance(self.evse, Unset):
            evse = self.evse.to_dict()

        instance = self.instance

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if custom_data is not UNSET:
            field_dict["customData"] = custom_data
        if evse is not UNSET:
            field_dict["evse"] = evse
        if instance is not UNSET:
            field_dict["instance"] = instance

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.custom_data_type import CustomDataType
        from ..models.evse_type import EvseType

        d = dict(src_dict)
        name = d.pop("name")

        _custom_data = d.pop("customData", UNSET)
        custom_data: CustomDataType | Unset
        if isinstance(_custom_data, Unset) or _custom_data is None:
            custom_data = UNSET
        else:
            custom_data = CustomDataType.from_dict(_custom_data)

        _evse = d.pop("evse", UNSET)
        evse: EvseType | Unset
        if isinstance(_evse, Unset) or _evse is None:
            evse = UNSET
        else:
            evse = EvseType.from_dict(_evse)

        instance = d.pop("instance", UNSET)

        component_type = cls(
            name=name,
            custom_data=custom_data,
            evse=evse,
            instance=instance,
        )

        component_type.additional_properties = d
        return component_type

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

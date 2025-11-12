from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.custom_data_type_additional_properties import CustomDataTypeAdditionalProperties


T = TypeVar("T", bound="CustomDataType")


@_attrs_define
class CustomDataType:
    """
    Attributes:
        vendor_id (str):
        additional_properties (CustomDataTypeAdditionalProperties | Unset):
    """

    vendor_id: str
    additional_properties: CustomDataTypeAdditionalProperties | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        vendor_id = self.vendor_id

        additional_properties: dict[str, Any] | Unset = UNSET
        if not isinstance(self.additional_properties, Unset):
            additional_properties = self.additional_properties.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "vendorId": vendor_id,
            }
        )
        if additional_properties is not UNSET:
            field_dict["additionalProperties"] = additional_properties

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.custom_data_type_additional_properties import CustomDataTypeAdditionalProperties

        d = dict(src_dict)
        vendor_id = d.pop("vendorId")

        _additional_properties = d.pop("additionalProperties", UNSET)
        additional_properties: CustomDataTypeAdditionalProperties | Unset
        if isinstance(_additional_properties, Unset) or _additional_properties is None:
            additional_properties = UNSET
        else:
            additional_properties = CustomDataTypeAdditionalProperties.from_dict(_additional_properties)

        custom_data_type = cls(
            vendor_id=vendor_id,
            additional_properties=additional_properties,
        )

        custom_data_type.additional_properties = d
        return custom_data_type

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

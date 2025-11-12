from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.set_variable_data_type_attribute_type import SetVariableDataTypeAttributeType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.component_type import ComponentType
    from ..models.custom_data_type import CustomDataType
    from ..models.variable_type import VariableType


T = TypeVar("T", bound="SetVariableDataType")


@_attrs_define
class SetVariableDataType:
    """
    Attributes:
        attribute_value (str):
        component (ComponentType):
        variable (VariableType):
        custom_data (CustomDataType | Unset):
        attribute_type (SetVariableDataTypeAttributeType | Unset):  Default: SetVariableDataTypeAttributeType.VALUE_0.
    """

    attribute_value: str
    component: ComponentType
    variable: VariableType
    custom_data: CustomDataType | Unset = UNSET
    attribute_type: SetVariableDataTypeAttributeType | Unset = SetVariableDataTypeAttributeType.VALUE_0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        attribute_value = self.attribute_value

        component = self.component.to_dict()

        variable = self.variable.to_dict()

        custom_data: dict[str, Any] | Unset = UNSET
        if not isinstance(self.custom_data, Unset):
            custom_data = self.custom_data.to_dict()

        attribute_type: int | Unset = UNSET
        if not isinstance(self.attribute_type, Unset):
            attribute_type = self.attribute_type.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "attributeValue": attribute_value,
                "component": component,
                "variable": variable,
            }
        )
        if custom_data is not UNSET:
            field_dict["customData"] = custom_data
        if attribute_type is not UNSET:
            field_dict["attributeType"] = attribute_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.component_type import ComponentType
        from ..models.custom_data_type import CustomDataType
        from ..models.variable_type import VariableType

        d = dict(src_dict)
        attribute_value = d.pop("attributeValue")

        component = ComponentType.from_dict(d.pop("component"))

        variable = VariableType.from_dict(d.pop("variable"))

        _custom_data = d.pop("customData", UNSET)
        custom_data: CustomDataType | Unset
        if isinstance(_custom_data, Unset) or _custom_data is None:
            custom_data = UNSET
        else:
            custom_data = CustomDataType.from_dict(_custom_data)

        _attribute_type = d.pop("attributeType", UNSET)
        attribute_type: SetVariableDataTypeAttributeType | Unset
        if isinstance(_attribute_type, Unset) or _attribute_type is None:
            attribute_type = UNSET
        else:
            attribute_type = SetVariableDataTypeAttributeType(_attribute_type)

        set_variable_data_type = cls(
            attribute_value=attribute_value,
            component=component,
            variable=variable,
            custom_data=custom_data,
            attribute_type=attribute_type,
        )

        set_variable_data_type.additional_properties = d
        return set_variable_data_type

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

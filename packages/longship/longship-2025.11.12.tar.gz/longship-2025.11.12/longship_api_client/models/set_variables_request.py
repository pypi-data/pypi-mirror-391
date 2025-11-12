from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.custom_data_type import CustomDataType
    from ..models.set_variable_data_type import SetVariableDataType


T = TypeVar("T", bound="SetVariablesRequest")


@_attrs_define
class SetVariablesRequest:
    """
    Attributes:
        set_variable_data (list[SetVariableDataType]):
        custom_data (CustomDataType | Unset):
    """

    set_variable_data: list[SetVariableDataType]
    custom_data: CustomDataType | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        set_variable_data = []
        for set_variable_data_item_data in self.set_variable_data:
            set_variable_data_item = set_variable_data_item_data.to_dict()
            set_variable_data.append(set_variable_data_item)

        custom_data: dict[str, Any] | Unset = UNSET
        if not isinstance(self.custom_data, Unset):
            custom_data = self.custom_data.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "setVariableData": set_variable_data,
            }
        )
        if custom_data is not UNSET:
            field_dict["customData"] = custom_data

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.custom_data_type import CustomDataType
        from ..models.set_variable_data_type import SetVariableDataType

        d = dict(src_dict)
        set_variable_data = []
        _set_variable_data = d.pop("setVariableData")
        for set_variable_data_item_data in _set_variable_data:
            set_variable_data_item = SetVariableDataType.from_dict(set_variable_data_item_data)

            set_variable_data.append(set_variable_data_item)

        _custom_data = d.pop("customData", UNSET)
        custom_data: CustomDataType | Unset
        if isinstance(_custom_data, Unset) or _custom_data is None:
            custom_data = UNSET
        else:
            custom_data = CustomDataType.from_dict(_custom_data)

        set_variables_request = cls(
            set_variable_data=set_variable_data,
            custom_data=custom_data,
        )

        set_variables_request.additional_properties = d
        return set_variables_request

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

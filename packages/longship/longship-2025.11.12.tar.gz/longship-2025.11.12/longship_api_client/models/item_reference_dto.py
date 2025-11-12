from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ItemReferenceDto")


@_attrs_define
class ItemReferenceDto:
    """
    Attributes:
        component_name (str | Unset):
        component_instance (str | Unset):
        evse_id (str | Unset):
        connector_id (str | Unset):
        variable_instance (str | Unset):
    """

    component_name: str | Unset = UNSET
    component_instance: str | Unset = UNSET
    evse_id: str | Unset = UNSET
    connector_id: str | Unset = UNSET
    variable_instance: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        component_name = self.component_name

        component_instance = self.component_instance

        evse_id = self.evse_id

        connector_id = self.connector_id

        variable_instance = self.variable_instance

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if component_name is not UNSET:
            field_dict["componentName"] = component_name
        if component_instance is not UNSET:
            field_dict["componentInstance"] = component_instance
        if evse_id is not UNSET:
            field_dict["evseId"] = evse_id
        if connector_id is not UNSET:
            field_dict["connectorId"] = connector_id
        if variable_instance is not UNSET:
            field_dict["variableInstance"] = variable_instance

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        component_name = d.pop("componentName", UNSET)

        component_instance = d.pop("componentInstance", UNSET)

        evse_id = d.pop("evseId", UNSET)

        connector_id = d.pop("connectorId", UNSET)

        variable_instance = d.pop("variableInstance", UNSET)

        item_reference_dto = cls(
            component_name=component_name,
            component_instance=component_instance,
            evse_id=evse_id,
            connector_id=connector_id,
            variable_instance=variable_instance,
        )

        item_reference_dto.additional_properties = d
        return item_reference_dto

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

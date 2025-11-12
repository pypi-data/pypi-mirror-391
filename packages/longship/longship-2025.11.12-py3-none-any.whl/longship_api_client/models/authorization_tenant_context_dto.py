from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AuthorizationTenantContextDto")


@_attrs_define
class AuthorizationTenantContextDto:
    """
    Attributes:
        hubject_priority (int | Unset):
        hubject_enabled (bool | Unset):
        hubject_fast_approval (bool | Unset):
    """

    hubject_priority: int | Unset = UNSET
    hubject_enabled: bool | Unset = UNSET
    hubject_fast_approval: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        hubject_priority = self.hubject_priority

        hubject_enabled = self.hubject_enabled

        hubject_fast_approval = self.hubject_fast_approval

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if hubject_priority is not UNSET:
            field_dict["hubjectPriority"] = hubject_priority
        if hubject_enabled is not UNSET:
            field_dict["hubjectEnabled"] = hubject_enabled
        if hubject_fast_approval is not UNSET:
            field_dict["hubjectFastApproval"] = hubject_fast_approval

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        hubject_priority = d.pop("hubjectPriority", UNSET)

        hubject_enabled = d.pop("hubjectEnabled", UNSET)

        hubject_fast_approval = d.pop("hubjectFastApproval", UNSET)

        authorization_tenant_context_dto = cls(
            hubject_priority=hubject_priority,
            hubject_enabled=hubject_enabled,
            hubject_fast_approval=hubject_fast_approval,
        )

        authorization_tenant_context_dto.additional_properties = d
        return authorization_tenant_context_dto

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

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OuIntegrationInfoDto")


@_attrs_define
class OuIntegrationInfoDto:
    """
    Attributes:
        external_reference (str | Unset):
        grid_owner_reference (str | Unset):
        tenant_reference (str | Unset):
        customer_reference (str | Unset):
    """

    external_reference: str | Unset = UNSET
    grid_owner_reference: str | Unset = UNSET
    tenant_reference: str | Unset = UNSET
    customer_reference: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        external_reference = self.external_reference

        grid_owner_reference = self.grid_owner_reference

        tenant_reference = self.tenant_reference

        customer_reference = self.customer_reference

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if external_reference is not UNSET:
            field_dict["externalReference"] = external_reference
        if grid_owner_reference is not UNSET:
            field_dict["gridOwnerReference"] = grid_owner_reference
        if tenant_reference is not UNSET:
            field_dict["tenantReference"] = tenant_reference
        if customer_reference is not UNSET:
            field_dict["customerReference"] = customer_reference

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        external_reference = d.pop("externalReference", UNSET)

        grid_owner_reference = d.pop("gridOwnerReference", UNSET)

        tenant_reference = d.pop("tenantReference", UNSET)

        customer_reference = d.pop("customerReference", UNSET)

        ou_integration_info_dto = cls(
            external_reference=external_reference,
            grid_owner_reference=grid_owner_reference,
            tenant_reference=tenant_reference,
            customer_reference=customer_reference,
        )

        ou_integration_info_dto.additional_properties = d
        return ou_integration_info_dto

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

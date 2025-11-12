from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.authorization_charger_context_dto import AuthorizationChargerContextDto
    from ..models.authorization_tenant_context_dto import AuthorizationTenantContextDto


T = TypeVar("T", bound="AuthorizationContextDetailsDto")


@_attrs_define
class AuthorizationContextDetailsDto:
    """
    Attributes:
        charger (AuthorizationChargerContextDto | Unset):
        tenant (AuthorizationTenantContextDto | Unset):
    """

    charger: AuthorizationChargerContextDto | Unset = UNSET
    tenant: AuthorizationTenantContextDto | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        charger: dict[str, Any] | Unset = UNSET
        if not isinstance(self.charger, Unset):
            charger = self.charger.to_dict()

        tenant: dict[str, Any] | Unset = UNSET
        if not isinstance(self.tenant, Unset):
            tenant = self.tenant.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if charger is not UNSET:
            field_dict["charger"] = charger
        if tenant is not UNSET:
            field_dict["tenant"] = tenant

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.authorization_charger_context_dto import AuthorizationChargerContextDto
        from ..models.authorization_tenant_context_dto import AuthorizationTenantContextDto

        d = dict(src_dict)
        _charger = d.pop("charger", UNSET)
        charger: AuthorizationChargerContextDto | Unset
        if isinstance(_charger, Unset) or _charger is None:
            charger = UNSET
        else:
            charger = AuthorizationChargerContextDto.from_dict(_charger)

        _tenant = d.pop("tenant", UNSET)
        tenant: AuthorizationTenantContextDto | Unset
        if isinstance(_tenant, Unset) or _tenant is None:
            tenant = UNSET
        else:
            tenant = AuthorizationTenantContextDto.from_dict(_tenant)

        authorization_context_details_dto = cls(
            charger=charger,
            tenant=tenant,
        )

        authorization_context_details_dto.additional_properties = d
        return authorization_context_details_dto

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

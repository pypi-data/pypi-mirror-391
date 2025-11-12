from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReimbursementCustomerShareDto")


@_attrs_define
class ReimbursementCustomerShareDto:
    """
    Attributes:
        customer_share (float | Unset):
        energy_compensation (float | Unset):
        tenant_fee (float | Unset):
    """

    customer_share: float | Unset = UNSET
    energy_compensation: float | Unset = UNSET
    tenant_fee: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        customer_share = self.customer_share

        energy_compensation = self.energy_compensation

        tenant_fee = self.tenant_fee

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if customer_share is not UNSET:
            field_dict["customerShare"] = customer_share
        if energy_compensation is not UNSET:
            field_dict["energyCompensation"] = energy_compensation
        if tenant_fee is not UNSET:
            field_dict["tenantFee"] = tenant_fee

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        customer_share = d.pop("customerShare", UNSET)

        energy_compensation = d.pop("energyCompensation", UNSET)

        tenant_fee = d.pop("tenantFee", UNSET)

        reimbursement_customer_share_dto = cls(
            customer_share=customer_share,
            energy_compensation=energy_compensation,
            tenant_fee=tenant_fee,
        )

        reimbursement_customer_share_dto.additional_properties = d
        return reimbursement_customer_share_dto

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

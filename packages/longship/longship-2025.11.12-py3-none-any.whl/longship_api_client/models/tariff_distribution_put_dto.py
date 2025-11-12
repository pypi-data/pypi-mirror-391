from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TariffDistributionPutDto")


@_attrs_define
class TariffDistributionPutDto:
    """
    Attributes:
        name (str | Unset):
        ou_code (str | Unset):
        energy_compensation (float | Unset):
        fixed_tenant_k_wh_fee (float | Unset):
        percentage_fee_customer (float | Unset):
        percentage_fee_tenant (float | Unset):
    """

    name: str | Unset = UNSET
    ou_code: str | Unset = UNSET
    energy_compensation: float | Unset = UNSET
    fixed_tenant_k_wh_fee: float | Unset = UNSET
    percentage_fee_customer: float | Unset = UNSET
    percentage_fee_tenant: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        ou_code = self.ou_code

        energy_compensation = self.energy_compensation

        fixed_tenant_k_wh_fee = self.fixed_tenant_k_wh_fee

        percentage_fee_customer = self.percentage_fee_customer

        percentage_fee_tenant = self.percentage_fee_tenant

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if ou_code is not UNSET:
            field_dict["ouCode"] = ou_code
        if energy_compensation is not UNSET:
            field_dict["energyCompensation"] = energy_compensation
        if fixed_tenant_k_wh_fee is not UNSET:
            field_dict["fixedTenantKWhFee"] = fixed_tenant_k_wh_fee
        if percentage_fee_customer is not UNSET:
            field_dict["percentageFeeCustomer"] = percentage_fee_customer
        if percentage_fee_tenant is not UNSET:
            field_dict["percentageFeeTenant"] = percentage_fee_tenant

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        ou_code = d.pop("ouCode", UNSET)

        energy_compensation = d.pop("energyCompensation", UNSET)

        fixed_tenant_k_wh_fee = d.pop("fixedTenantKWhFee", UNSET)

        percentage_fee_customer = d.pop("percentageFeeCustomer", UNSET)

        percentage_fee_tenant = d.pop("percentageFeeTenant", UNSET)

        tariff_distribution_put_dto = cls(
            name=name,
            ou_code=ou_code,
            energy_compensation=energy_compensation,
            fixed_tenant_k_wh_fee=fixed_tenant_k_wh_fee,
            percentage_fee_customer=percentage_fee_customer,
            percentage_fee_tenant=percentage_fee_tenant,
        )

        tariff_distribution_put_dto.additional_properties = d
        return tariff_distribution_put_dto

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

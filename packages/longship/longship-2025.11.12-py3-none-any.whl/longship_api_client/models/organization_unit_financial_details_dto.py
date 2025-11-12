from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OrganizationUnitFinancialDetailsDto")


@_attrs_define
class OrganizationUnitFinancialDetailsDto:
    """
    Attributes:
        beneficiary_name (str | Unset):
        iban (str | Unset):
        bic (str | Unset):
    """

    beneficiary_name: str | Unset = UNSET
    iban: str | Unset = UNSET
    bic: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        beneficiary_name = self.beneficiary_name

        iban = self.iban

        bic = self.bic

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if beneficiary_name is not UNSET:
            field_dict["beneficiaryName"] = beneficiary_name
        if iban is not UNSET:
            field_dict["iban"] = iban
        if bic is not UNSET:
            field_dict["bic"] = bic

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        beneficiary_name = d.pop("beneficiaryName", UNSET)

        iban = d.pop("iban", UNSET)

        bic = d.pop("bic", UNSET)

        organization_unit_financial_details_dto = cls(
            beneficiary_name=beneficiary_name,
            iban=iban,
            bic=bic,
        )

        organization_unit_financial_details_dto.additional_properties = d
        return organization_unit_financial_details_dto

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

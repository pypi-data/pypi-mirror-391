from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReimbursementPriceDto")


@_attrs_define
class ReimbursementPriceDto:
    """
    Attributes:
        excl_vat (float | Unset):
        incl_vat (float | Unset):
    """

    excl_vat: float | Unset = UNSET
    incl_vat: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        excl_vat = self.excl_vat

        incl_vat = self.incl_vat

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if excl_vat is not UNSET:
            field_dict["excl_vat"] = excl_vat
        if incl_vat is not UNSET:
            field_dict["incl_vat"] = incl_vat

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        excl_vat = d.pop("excl_vat", UNSET)

        incl_vat = d.pop("incl_vat", UNSET)

        reimbursement_price_dto = cls(
            excl_vat=excl_vat,
            incl_vat=incl_vat,
        )

        reimbursement_price_dto.additional_properties = d
        return reimbursement_price_dto

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

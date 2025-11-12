from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.environmental_impact_dto_category import EnvironmentalImpactDtoCategory
from ..types import UNSET, Unset

T = TypeVar("T", bound="EnvironmentalImpactDto")


@_attrs_define
class EnvironmentalImpactDto:
    """
    Attributes:
        category (EnvironmentalImpactDtoCategory | Unset):  Default: EnvironmentalImpactDtoCategory.NUCLEAR_WASTE.
        amount (int | Unset):
    """

    category: EnvironmentalImpactDtoCategory | Unset = EnvironmentalImpactDtoCategory.NUCLEAR_WASTE
    amount: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        category: str | Unset = UNSET
        if not isinstance(self.category, Unset):
            category = self.category.value

        amount = self.amount

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if category is not UNSET:
            field_dict["category"] = category
        if amount is not UNSET:
            field_dict["amount"] = amount

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _category = d.pop("category", UNSET)
        category: EnvironmentalImpactDtoCategory | Unset
        if isinstance(_category, Unset) or _category is None:
            category = UNSET
        else:
            category = EnvironmentalImpactDtoCategory(_category)

        amount = d.pop("amount", UNSET)

        environmental_impact_dto = cls(
            category=category,
            amount=amount,
        )

        environmental_impact_dto.additional_properties = d
        return environmental_impact_dto

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

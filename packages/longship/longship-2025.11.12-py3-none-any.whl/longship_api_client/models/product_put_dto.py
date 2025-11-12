from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ProductPutDto")


@_attrs_define
class ProductPutDto:
    """
    Attributes:
        ou (str):
        name (str | Unset):
        price (float | Unset):
        description (str | Unset):
    """

    ou: str
    name: str | Unset = UNSET
    price: float | Unset = UNSET
    description: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ou = self.ou

        name = self.name

        price = self.price

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ou": ou,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if price is not UNSET:
            field_dict["price"] = price
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ou = d.pop("ou")

        name = d.pop("name", UNSET)

        price = d.pop("price", UNSET)

        description = d.pop("description", UNSET)

        product_put_dto = cls(
            ou=ou,
            name=name,
            price=price,
            description=description,
        )

        product_put_dto.additional_properties = d
        return product_put_dto

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

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.price_component_pricing_type import PriceComponentPricingType
from ..types import UNSET, Unset

T = TypeVar("T", bound="PriceComponent")


@_attrs_define
class PriceComponent:
    """
    Attributes:
        pricing_type (PriceComponentPricingType):  Default: PriceComponentPricingType.ENERGY.
        price (float | Unset):
        step_size (int | Unset):
        vat (float | Unset):
    """

    pricing_type: PriceComponentPricingType = PriceComponentPricingType.ENERGY
    price: float | Unset = UNSET
    step_size: int | Unset = UNSET
    vat: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        pricing_type = self.pricing_type.value

        price = self.price

        step_size = self.step_size

        vat = self.vat

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "pricingType": pricing_type,
            }
        )
        if price is not UNSET:
            field_dict["price"] = price
        if step_size is not UNSET:
            field_dict["stepSize"] = step_size
        if vat is not UNSET:
            field_dict["vat"] = vat

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        pricing_type = PriceComponentPricingType(d.pop("pricingType"))

        price = d.pop("price", UNSET)

        step_size = d.pop("stepSize", UNSET)

        vat = d.pop("vat", UNSET)

        price_component = cls(
            pricing_type=pricing_type,
            price=price,
            step_size=step_size,
            vat=vat,
        )

        price_component.additional_properties = d
        return price_component

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

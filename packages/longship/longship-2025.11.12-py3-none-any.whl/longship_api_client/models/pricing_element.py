from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.price_component import PriceComponent
    from ..models.tariff_restriction import TariffRestriction


T = TypeVar("T", bound="PricingElement")


@_attrs_define
class PricingElement:
    """
    Attributes:
        price_components (list[PriceComponent] | Unset):
        tariff_restriction (TariffRestriction | Unset):
    """

    price_components: list[PriceComponent] | Unset = UNSET
    tariff_restriction: TariffRestriction | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        price_components: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.price_components, Unset):
            price_components = []
            for price_components_item_data in self.price_components:
                price_components_item = price_components_item_data.to_dict()
                price_components.append(price_components_item)

        tariff_restriction: dict[str, Any] | Unset = UNSET
        if not isinstance(self.tariff_restriction, Unset):
            tariff_restriction = self.tariff_restriction.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if price_components is not UNSET:
            field_dict["priceComponents"] = price_components
        if tariff_restriction is not UNSET:
            field_dict["tariffRestriction"] = tariff_restriction

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.price_component import PriceComponent
        from ..models.tariff_restriction import TariffRestriction

        d = dict(src_dict)
        price_components = []
        _price_components = d.pop("priceComponents", UNSET)
        for price_components_item_data in _price_components or []:
            price_components_item = PriceComponent.from_dict(price_components_item_data)

            price_components.append(price_components_item)

        _tariff_restriction = d.pop("tariffRestriction", UNSET)
        tariff_restriction: TariffRestriction | Unset
        if isinstance(_tariff_restriction, Unset) or _tariff_restriction is None:
            tariff_restriction = UNSET
        else:
            tariff_restriction = TariffRestriction.from_dict(_tariff_restriction)

        pricing_element = cls(
            price_components=price_components,
            tariff_restriction=tariff_restriction,
        )

        pricing_element.additional_properties = d
        return pricing_element

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

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.energy_source_dto_source import EnergySourceDtoSource
from ..types import UNSET, Unset

T = TypeVar("T", bound="EnergySourceDto")


@_attrs_define
class EnergySourceDto:
    """
    Attributes:
        source (EnergySourceDtoSource | Unset):  Default: EnergySourceDtoSource.NUCLEAR.
        percentage (int | Unset):
    """

    source: EnergySourceDtoSource | Unset = EnergySourceDtoSource.NUCLEAR
    percentage: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        source: str | Unset = UNSET
        if not isinstance(self.source, Unset):
            source = self.source.value

        percentage = self.percentage

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if source is not UNSET:
            field_dict["source"] = source
        if percentage is not UNSET:
            field_dict["percentage"] = percentage

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _source = d.pop("source", UNSET)
        source: EnergySourceDtoSource | Unset
        if isinstance(_source, Unset) or _source is None:
            source = UNSET
        else:
            source = EnergySourceDtoSource(_source)

        percentage = d.pop("percentage", UNSET)

        energy_source_dto = cls(
            source=source,
            percentage=percentage,
        )

        energy_source_dto.additional_properties = d
        return energy_source_dto

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

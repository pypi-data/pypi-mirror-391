from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.energy_source_dto import EnergySourceDto
    from ..models.environmental_impact_dto import EnvironmentalImpactDto


T = TypeVar("T", bound="EnergyMixDto")


@_attrs_define
class EnergyMixDto:
    """
    Attributes:
        is_green_energy (bool | Unset):
        energy_sources (list[EnergySourceDto] | Unset):
        environ_impact (list[EnvironmentalImpactDto] | Unset):
    """

    is_green_energy: bool | Unset = UNSET
    energy_sources: list[EnergySourceDto] | Unset = UNSET
    environ_impact: list[EnvironmentalImpactDto] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        is_green_energy = self.is_green_energy

        energy_sources: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.energy_sources, Unset):
            energy_sources = []
            for energy_sources_item_data in self.energy_sources:
                energy_sources_item = energy_sources_item_data.to_dict()
                energy_sources.append(energy_sources_item)

        environ_impact: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.environ_impact, Unset):
            environ_impact = []
            for environ_impact_item_data in self.environ_impact:
                environ_impact_item = environ_impact_item_data.to_dict()
                environ_impact.append(environ_impact_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if is_green_energy is not UNSET:
            field_dict["is_green_energy"] = is_green_energy
        if energy_sources is not UNSET:
            field_dict["energy_sources"] = energy_sources
        if environ_impact is not UNSET:
            field_dict["environ_impact"] = environ_impact

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.energy_source_dto import EnergySourceDto
        from ..models.environmental_impact_dto import EnvironmentalImpactDto

        d = dict(src_dict)
        is_green_energy = d.pop("is_green_energy", UNSET)

        energy_sources = []
        _energy_sources = d.pop("energy_sources", UNSET)
        for energy_sources_item_data in _energy_sources or []:
            energy_sources_item = EnergySourceDto.from_dict(energy_sources_item_data)

            energy_sources.append(energy_sources_item)

        environ_impact = []
        _environ_impact = d.pop("environ_impact", UNSET)
        for environ_impact_item_data in _environ_impact or []:
            environ_impact_item = EnvironmentalImpactDto.from_dict(environ_impact_item_data)

            environ_impact.append(environ_impact_item)

        energy_mix_dto = cls(
            is_green_energy=is_green_energy,
            energy_sources=energy_sources,
            environ_impact=environ_impact,
        )

        energy_mix_dto.additional_properties = d
        return energy_mix_dto

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

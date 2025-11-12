from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.exceptional_period_dto import ExceptionalPeriodDto
    from ..models.regular_hours_dto import RegularHoursDto


T = TypeVar("T", bound="HoursDto")


@_attrs_define
class HoursDto:
    """
    Attributes:
        twentyfourseven (bool | Unset):
        regular_hours (list[RegularHoursDto] | Unset):
        exceptional_openings (list[ExceptionalPeriodDto] | Unset):
        exceptional_closings (list[ExceptionalPeriodDto] | Unset):
    """

    twentyfourseven: bool | Unset = UNSET
    regular_hours: list[RegularHoursDto] | Unset = UNSET
    exceptional_openings: list[ExceptionalPeriodDto] | Unset = UNSET
    exceptional_closings: list[ExceptionalPeriodDto] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        twentyfourseven = self.twentyfourseven

        regular_hours: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.regular_hours, Unset):
            regular_hours = []
            for regular_hours_item_data in self.regular_hours:
                regular_hours_item = regular_hours_item_data.to_dict()
                regular_hours.append(regular_hours_item)

        exceptional_openings: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.exceptional_openings, Unset):
            exceptional_openings = []
            for exceptional_openings_item_data in self.exceptional_openings:
                exceptional_openings_item = exceptional_openings_item_data.to_dict()
                exceptional_openings.append(exceptional_openings_item)

        exceptional_closings: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.exceptional_closings, Unset):
            exceptional_closings = []
            for exceptional_closings_item_data in self.exceptional_closings:
                exceptional_closings_item = exceptional_closings_item_data.to_dict()
                exceptional_closings.append(exceptional_closings_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if twentyfourseven is not UNSET:
            field_dict["twentyfourseven"] = twentyfourseven
        if regular_hours is not UNSET:
            field_dict["regular_hours"] = regular_hours
        if exceptional_openings is not UNSET:
            field_dict["exceptional_openings"] = exceptional_openings
        if exceptional_closings is not UNSET:
            field_dict["exceptional_closings"] = exceptional_closings

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.exceptional_period_dto import ExceptionalPeriodDto
        from ..models.regular_hours_dto import RegularHoursDto

        d = dict(src_dict)
        twentyfourseven = d.pop("twentyfourseven", UNSET)

        regular_hours = []
        _regular_hours = d.pop("regular_hours", UNSET)
        for regular_hours_item_data in _regular_hours or []:
            regular_hours_item = RegularHoursDto.from_dict(regular_hours_item_data)

            regular_hours.append(regular_hours_item)

        exceptional_openings = []
        _exceptional_openings = d.pop("exceptional_openings", UNSET)
        for exceptional_openings_item_data in _exceptional_openings or []:
            exceptional_openings_item = ExceptionalPeriodDto.from_dict(exceptional_openings_item_data)

            exceptional_openings.append(exceptional_openings_item)

        exceptional_closings = []
        _exceptional_closings = d.pop("exceptional_closings", UNSET)
        for exceptional_closings_item_data in _exceptional_closings or []:
            exceptional_closings_item = ExceptionalPeriodDto.from_dict(exceptional_closings_item_data)

            exceptional_closings.append(exceptional_closings_item)

        hours_dto = cls(
            twentyfourseven=twentyfourseven,
            regular_hours=regular_hours,
            exceptional_openings=exceptional_openings,
            exceptional_closings=exceptional_closings,
        )

        hours_dto.additional_properties = d
        return hours_dto

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

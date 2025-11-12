from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="StringSegment")


@_attrs_define
class StringSegment:
    """
    Attributes:
        buffer (str | Unset):
        offset (int | Unset):
        length (int | Unset):
        value (str | Unset):
        has_value (bool | Unset):
    """

    buffer: str | Unset = UNSET
    offset: int | Unset = UNSET
    length: int | Unset = UNSET
    value: str | Unset = UNSET
    has_value: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        buffer = self.buffer

        offset = self.offset

        length = self.length

        value = self.value

        has_value = self.has_value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if buffer is not UNSET:
            field_dict["buffer"] = buffer
        if offset is not UNSET:
            field_dict["offset"] = offset
        if length is not UNSET:
            field_dict["length"] = length
        if value is not UNSET:
            field_dict["value"] = value
        if has_value is not UNSET:
            field_dict["hasValue"] = has_value

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        buffer = d.pop("buffer", UNSET)

        offset = d.pop("offset", UNSET)

        length = d.pop("length", UNSET)

        value = d.pop("value", UNSET)

        has_value = d.pop("hasValue", UNSET)

        string_segment = cls(
            buffer=buffer,
            offset=offset,
            length=length,
            value=value,
            has_value=has_value,
        )

        string_segment.additional_properties = d
        return string_segment

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

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.string_segment import StringSegment


T = TypeVar("T", bound="EntityTagHeaderValue")


@_attrs_define
class EntityTagHeaderValue:
    """
    Attributes:
        tag (StringSegment | Unset):
        is_weak (bool | Unset):
    """

    tag: StringSegment | Unset = UNSET
    is_weak: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tag: dict[str, Any] | Unset = UNSET
        if not isinstance(self.tag, Unset):
            tag = self.tag.to_dict()

        is_weak = self.is_weak

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if tag is not UNSET:
            field_dict["tag"] = tag
        if is_weak is not UNSET:
            field_dict["isWeak"] = is_weak

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.string_segment import StringSegment

        d = dict(src_dict)
        _tag = d.pop("tag", UNSET)
        tag: StringSegment | Unset
        if isinstance(_tag, Unset) or _tag is None:
            tag = UNSET
        else:
            tag = StringSegment.from_dict(_tag)

        is_weak = d.pop("isWeak", UNSET)

        entity_tag_header_value = cls(
            tag=tag,
            is_weak=is_weak,
        )

        entity_tag_header_value.additional_properties = d
        return entity_tag_header_value

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

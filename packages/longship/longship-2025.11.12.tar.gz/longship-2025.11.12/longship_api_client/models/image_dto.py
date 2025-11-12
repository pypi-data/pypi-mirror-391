from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.image_dto_category import ImageDtoCategory
from ..types import UNSET, Unset

T = TypeVar("T", bound="ImageDto")


@_attrs_define
class ImageDto:
    """
    Attributes:
        url (str | Unset):
        thumbnail (str | Unset):
        category (ImageDtoCategory | Unset):  Default: ImageDtoCategory.CHARGER.
        type_ (str | Unset):
        width (int | Unset):
        height (int | Unset):
    """

    url: str | Unset = UNSET
    thumbnail: str | Unset = UNSET
    category: ImageDtoCategory | Unset = ImageDtoCategory.CHARGER
    type_: str | Unset = UNSET
    width: int | Unset = UNSET
    height: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        thumbnail = self.thumbnail

        category: str | Unset = UNSET
        if not isinstance(self.category, Unset):
            category = self.category.value

        type_ = self.type_

        width = self.width

        height = self.height

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if url is not UNSET:
            field_dict["url"] = url
        if thumbnail is not UNSET:
            field_dict["thumbnail"] = thumbnail
        if category is not UNSET:
            field_dict["category"] = category
        if type_ is not UNSET:
            field_dict["type"] = type_
        if width is not UNSET:
            field_dict["width"] = width
        if height is not UNSET:
            field_dict["height"] = height

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("url", UNSET)

        thumbnail = d.pop("thumbnail", UNSET)

        _category = d.pop("category", UNSET)
        category: ImageDtoCategory | Unset
        if isinstance(_category, Unset) or _category is None:
            category = UNSET
        else:
            category = ImageDtoCategory(_category)

        type_ = d.pop("type", UNSET)

        width = d.pop("width", UNSET)

        height = d.pop("height", UNSET)

        image_dto = cls(
            url=url,
            thumbnail=thumbnail,
            category=category,
            type_=type_,
            width=width,
            height=height,
        )

        image_dto.additional_properties = d
        return image_dto

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

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.image_dto import ImageDto


T = TypeVar("T", bound="BusinessDetailsDto")


@_attrs_define
class BusinessDetailsDto:
    """
    Attributes:
        name (str | Unset):
        website (str | Unset):
        image (ImageDto | Unset):
    """

    name: str | Unset = UNSET
    website: str | Unset = UNSET
    image: ImageDto | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        website = self.website

        image: dict[str, Any] | Unset = UNSET
        if not isinstance(self.image, Unset):
            image = self.image.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if website is not UNSET:
            field_dict["website"] = website
        if image is not UNSET:
            field_dict["image"] = image

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.image_dto import ImageDto

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        website = d.pop("website", UNSET)

        _image = d.pop("image", UNSET)
        image: ImageDto | Unset
        if isinstance(_image, Unset) or _image is None:
            image = UNSET
        else:
            image = ImageDto.from_dict(_image)

        business_details_dto = cls(
            name=name,
            website=website,
            image=image,
        )

        business_details_dto.additional_properties = d
        return business_details_dto

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

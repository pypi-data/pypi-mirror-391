from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.id_tag_info import IdTagInfo


T = TypeVar("T", bound="AuthorizationData")


@_attrs_define
class AuthorizationData:
    """
    Attributes:
        id_tag (str):
        id_tag_info (IdTagInfo | Unset):
    """

    id_tag: str
    id_tag_info: IdTagInfo | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id_tag = self.id_tag

        id_tag_info: dict[str, Any] | Unset = UNSET
        if not isinstance(self.id_tag_info, Unset):
            id_tag_info = self.id_tag_info.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "idTag": id_tag,
            }
        )
        if id_tag_info is not UNSET:
            field_dict["idTagInfo"] = id_tag_info

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.id_tag_info import IdTagInfo

        d = dict(src_dict)
        id_tag = d.pop("idTag")

        _id_tag_info = d.pop("idTagInfo", UNSET)
        id_tag_info: IdTagInfo | Unset
        if isinstance(_id_tag_info, Unset) or _id_tag_info is None:
            id_tag_info = UNSET
        else:
            id_tag_info = IdTagInfo.from_dict(_id_tag_info)

        authorization_data = cls(
            id_tag=id_tag,
            id_tag_info=id_tag_info,
        )

        authorization_data.additional_properties = d
        return authorization_data

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

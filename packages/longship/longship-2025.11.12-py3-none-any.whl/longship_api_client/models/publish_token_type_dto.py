from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.publish_token_type_dto_type import PublishTokenTypeDtoType
from ..types import UNSET, Unset

T = TypeVar("T", bound="PublishTokenTypeDto")


@_attrs_define
class PublishTokenTypeDto:
    """
    Attributes:
        uid (str | Unset):
        type_ (PublishTokenTypeDtoType | Unset):  Default: PublishTokenTypeDtoType.RFID.
        visual_number (str | Unset):
        issuer (str | Unset):
        group_id (str | Unset):
    """

    uid: str | Unset = UNSET
    type_: PublishTokenTypeDtoType | Unset = PublishTokenTypeDtoType.RFID
    visual_number: str | Unset = UNSET
    issuer: str | Unset = UNSET
    group_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uid = self.uid

        type_: str | Unset = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        visual_number = self.visual_number

        issuer = self.issuer

        group_id = self.group_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if uid is not UNSET:
            field_dict["uid"] = uid
        if type_ is not UNSET:
            field_dict["type"] = type_
        if visual_number is not UNSET:
            field_dict["visual_number"] = visual_number
        if issuer is not UNSET:
            field_dict["issuer"] = issuer
        if group_id is not UNSET:
            field_dict["group_id"] = group_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        uid = d.pop("uid", UNSET)

        _type_ = d.pop("type", UNSET)
        type_: PublishTokenTypeDtoType | Unset
        if isinstance(_type_, Unset) or _type_ is None:
            type_ = UNSET
        else:
            type_ = PublishTokenTypeDtoType(_type_)

        visual_number = d.pop("visual_number", UNSET)

        issuer = d.pop("issuer", UNSET)

        group_id = d.pop("group_id", UNSET)

        publish_token_type_dto = cls(
            uid=uid,
            type_=type_,
            visual_number=visual_number,
            issuer=issuer,
            group_id=group_id,
        )

        publish_token_type_dto.additional_properties = d
        return publish_token_type_dto

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

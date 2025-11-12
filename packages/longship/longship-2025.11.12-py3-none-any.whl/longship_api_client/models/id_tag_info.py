from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.id_tag_info_status import IdTagInfoStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="IdTagInfo")


@_attrs_define
class IdTagInfo:
    """
    Attributes:
        status (IdTagInfoStatus):  Default: IdTagInfoStatus.ACCEPTED.
        expiry_date (datetime.datetime | Unset):
        parent_id_tag (str | Unset):
    """

    status: IdTagInfoStatus = IdTagInfoStatus.ACCEPTED
    expiry_date: datetime.datetime | Unset = UNSET
    parent_id_tag: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status.value

        expiry_date: str | Unset = UNSET
        if not isinstance(self.expiry_date, Unset):
            expiry_date = self.expiry_date.isoformat()

        parent_id_tag = self.parent_id_tag

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
            }
        )
        if expiry_date is not UNSET:
            field_dict["expiryDate"] = expiry_date
        if parent_id_tag is not UNSET:
            field_dict["parentIdTag"] = parent_id_tag

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        status = IdTagInfoStatus(d.pop("status"))

        _expiry_date = d.pop("expiryDate", UNSET)
        expiry_date: datetime.datetime | Unset
        if isinstance(_expiry_date, Unset) or _expiry_date is None:
            expiry_date = UNSET
        else:
            expiry_date = isoparse(_expiry_date)

        parent_id_tag = d.pop("parentIdTag", UNSET)

        id_tag_info = cls(
            status=status,
            expiry_date=expiry_date,
            parent_id_tag=parent_id_tag,
        )

        id_tag_info.additional_properties = d
        return id_tag_info

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

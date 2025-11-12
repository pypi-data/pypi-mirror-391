from __future__ import annotations

import datetime
from collections.abc import Mapping
from io import BytesIO
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, File, FileTypes, Unset

if TYPE_CHECKING:
    from ..models.entity_tag_header_value import EntityTagHeaderValue


T = TypeVar("T", bound="FileContentResult")


@_attrs_define
class FileContentResult:
    """
    Attributes:
        file_contents (File | Unset):
        content_type (str | Unset):
        file_download_name (str | Unset):
        last_modified (datetime.datetime | Unset):
        entity_tag (EntityTagHeaderValue | Unset):
        enable_range_processing (bool | Unset):
    """

    file_contents: File | Unset = UNSET
    content_type: str | Unset = UNSET
    file_download_name: str | Unset = UNSET
    last_modified: datetime.datetime | Unset = UNSET
    entity_tag: EntityTagHeaderValue | Unset = UNSET
    enable_range_processing: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        file_contents: FileTypes | Unset = UNSET
        if not isinstance(self.file_contents, Unset):
            file_contents = self.file_contents.to_tuple()

        content_type = self.content_type

        file_download_name = self.file_download_name

        last_modified: str | Unset = UNSET
        if not isinstance(self.last_modified, Unset):
            last_modified = self.last_modified.isoformat()

        entity_tag: dict[str, Any] | Unset = UNSET
        if not isinstance(self.entity_tag, Unset):
            entity_tag = self.entity_tag.to_dict()

        enable_range_processing = self.enable_range_processing

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if file_contents is not UNSET:
            field_dict["fileContents"] = file_contents
        if content_type is not UNSET:
            field_dict["contentType"] = content_type
        if file_download_name is not UNSET:
            field_dict["fileDownloadName"] = file_download_name
        if last_modified is not UNSET:
            field_dict["lastModified"] = last_modified
        if entity_tag is not UNSET:
            field_dict["entityTag"] = entity_tag
        if enable_range_processing is not UNSET:
            field_dict["enableRangeProcessing"] = enable_range_processing

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.entity_tag_header_value import EntityTagHeaderValue

        d = dict(src_dict)
        _file_contents = d.pop("fileContents", UNSET)
        file_contents: File | Unset
        if isinstance(_file_contents, Unset) or _file_contents is None:
            file_contents = UNSET
        else:
            file_contents = File(payload=BytesIO(_file_contents))

        content_type = d.pop("contentType", UNSET)

        file_download_name = d.pop("fileDownloadName", UNSET)

        _last_modified = d.pop("lastModified", UNSET)
        last_modified: datetime.datetime | Unset
        if isinstance(_last_modified, Unset) or _last_modified is None:
            last_modified = UNSET
        else:
            last_modified = isoparse(_last_modified)

        _entity_tag = d.pop("entityTag", UNSET)
        entity_tag: EntityTagHeaderValue | Unset
        if isinstance(_entity_tag, Unset) or _entity_tag is None:
            entity_tag = UNSET
        else:
            entity_tag = EntityTagHeaderValue.from_dict(_entity_tag)

        enable_range_processing = d.pop("enableRangeProcessing", UNSET)

        file_content_result = cls(
            file_contents=file_contents,
            content_type=content_type,
            file_download_name=file_download_name,
            last_modified=last_modified,
            entity_tag=entity_tag,
            enable_range_processing=enable_range_processing,
        )

        file_content_result.additional_properties = d
        return file_content_result

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

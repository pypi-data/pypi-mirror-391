from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.webhook_summary_get_dto_event_types_item import WebhookSummaryGetDtoEventTypesItem
from ..types import UNSET, Unset

T = TypeVar("T", bound="WebhookSummaryGetDto")


@_attrs_define
class WebhookSummaryGetDto:
    """
    Attributes:
        id (str | Unset):
        name (str | Unset):
        enabled (bool | Unset):
        event_types (list[WebhookSummaryGetDtoEventTypesItem] | Unset):
        created (datetime.datetime | Unset):
        updated (datetime.datetime | Unset):
    """

    id: str | Unset = UNSET
    name: str | Unset = UNSET
    enabled: bool | Unset = UNSET
    event_types: list[WebhookSummaryGetDtoEventTypesItem] | Unset = UNSET
    created: datetime.datetime | Unset = UNSET
    updated: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        enabled = self.enabled

        event_types: list[str] | Unset = UNSET
        if not isinstance(self.event_types, Unset):
            event_types = []
            for event_types_item_data in self.event_types:
                event_types_item = event_types_item_data.value
                event_types.append(event_types_item)

        created: str | Unset = UNSET
        if not isinstance(self.created, Unset):
            created = self.created.isoformat()

        updated: str | Unset = UNSET
        if not isinstance(self.updated, Unset):
            updated = self.updated.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if event_types is not UNSET:
            field_dict["eventTypes"] = event_types
        if created is not UNSET:
            field_dict["created"] = created
        if updated is not UNSET:
            field_dict["updated"] = updated

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        enabled = d.pop("enabled", UNSET)

        event_types = []
        _event_types = d.pop("eventTypes", UNSET)
        for event_types_item_data in _event_types or []:
            event_types_item = WebhookSummaryGetDtoEventTypesItem(event_types_item_data)

            event_types.append(event_types_item)

        _created = d.pop("created", UNSET)
        created: datetime.datetime | Unset
        if isinstance(_created, Unset) or _created is None:
            created = UNSET
        else:
            created = isoparse(_created)

        _updated = d.pop("updated", UNSET)
        updated: datetime.datetime | Unset
        if isinstance(_updated, Unset) or _updated is None:
            updated = UNSET
        else:
            updated = isoparse(_updated)

        webhook_summary_get_dto = cls(
            id=id,
            name=name,
            enabled=enabled,
            event_types=event_types,
            created=created,
            updated=updated,
        )

        webhook_summary_get_dto.additional_properties = d
        return webhook_summary_get_dto

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

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.webhook_put_dto_event_types_item import WebhookPutDtoEventTypesItem
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.webhook_header_dto import WebhookHeaderDto


T = TypeVar("T", bound="WebhookPutDto")


@_attrs_define
class WebhookPutDto:
    """
    Attributes:
        name (str | Unset):
        ou_code (str | Unset):
        url (str | Unset):
        enabled (bool | Unset):
        event_types (list[WebhookPutDtoEventTypesItem] | Unset):
        headers (list[WebhookHeaderDto] | Unset):
    """

    name: str | Unset = UNSET
    ou_code: str | Unset = UNSET
    url: str | Unset = UNSET
    enabled: bool | Unset = UNSET
    event_types: list[WebhookPutDtoEventTypesItem] | Unset = UNSET
    headers: list[WebhookHeaderDto] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        ou_code = self.ou_code

        url = self.url

        enabled = self.enabled

        event_types: list[str] | Unset = UNSET
        if not isinstance(self.event_types, Unset):
            event_types = []
            for event_types_item_data in self.event_types:
                event_types_item = event_types_item_data.value
                event_types.append(event_types_item)

        headers: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.headers, Unset):
            headers = []
            for headers_item_data in self.headers:
                headers_item = headers_item_data.to_dict()
                headers.append(headers_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if ou_code is not UNSET:
            field_dict["ouCode"] = ou_code
        if url is not UNSET:
            field_dict["url"] = url
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if event_types is not UNSET:
            field_dict["eventTypes"] = event_types
        if headers is not UNSET:
            field_dict["headers"] = headers

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.webhook_header_dto import WebhookHeaderDto

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        ou_code = d.pop("ouCode", UNSET)

        url = d.pop("url", UNSET)

        enabled = d.pop("enabled", UNSET)

        event_types = []
        _event_types = d.pop("eventTypes", UNSET)
        for event_types_item_data in _event_types or []:
            event_types_item = WebhookPutDtoEventTypesItem(event_types_item_data)

            event_types.append(event_types_item)

        headers = []
        _headers = d.pop("headers", UNSET)
        for headers_item_data in _headers or []:
            headers_item = WebhookHeaderDto.from_dict(headers_item_data)

            headers.append(headers_item)

        webhook_put_dto = cls(
            name=name,
            ou_code=ou_code,
            url=url,
            enabled=enabled,
            event_types=event_types,
            headers=headers,
        )

        webhook_put_dto.additional_properties = d
        return webhook_put_dto

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

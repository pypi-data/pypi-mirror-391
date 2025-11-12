from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.item_characteristics_dto import ItemCharacteristicsDto
    from ..models.item_reference_dto import ItemReferenceDto


T = TypeVar("T", bound="ChargepointConfigurationItemsDto")


@_attrs_define
class ChargepointConfigurationItemsDto:
    """
    Attributes:
        id (str | Unset):
        read_only (bool | Unset):
        value (str | Unset):
        name (str | Unset):
        item_reference (ItemReferenceDto | Unset):
        item_characteristics (ItemCharacteristicsDto | Unset):
        created (datetime.datetime | Unset):
        modified (datetime.datetime | Unset):
        deleted (datetime.datetime | Unset):
    """

    id: str | Unset = UNSET
    read_only: bool | Unset = UNSET
    value: str | Unset = UNSET
    name: str | Unset = UNSET
    item_reference: ItemReferenceDto | Unset = UNSET
    item_characteristics: ItemCharacteristicsDto | Unset = UNSET
    created: datetime.datetime | Unset = UNSET
    modified: datetime.datetime | Unset = UNSET
    deleted: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        read_only = self.read_only

        value = self.value

        name = self.name

        item_reference: dict[str, Any] | Unset = UNSET
        if not isinstance(self.item_reference, Unset):
            item_reference = self.item_reference.to_dict()

        item_characteristics: dict[str, Any] | Unset = UNSET
        if not isinstance(self.item_characteristics, Unset):
            item_characteristics = self.item_characteristics.to_dict()

        created: str | Unset = UNSET
        if not isinstance(self.created, Unset):
            created = self.created.isoformat()

        modified: str | Unset = UNSET
        if not isinstance(self.modified, Unset):
            modified = self.modified.isoformat()

        deleted: str | Unset = UNSET
        if not isinstance(self.deleted, Unset):
            deleted = self.deleted.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if read_only is not UNSET:
            field_dict["readOnly"] = read_only
        if value is not UNSET:
            field_dict["value"] = value
        if name is not UNSET:
            field_dict["name"] = name
        if item_reference is not UNSET:
            field_dict["itemReference"] = item_reference
        if item_characteristics is not UNSET:
            field_dict["itemCharacteristics"] = item_characteristics
        if created is not UNSET:
            field_dict["created"] = created
        if modified is not UNSET:
            field_dict["modified"] = modified
        if deleted is not UNSET:
            field_dict["deleted"] = deleted

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.item_characteristics_dto import ItemCharacteristicsDto
        from ..models.item_reference_dto import ItemReferenceDto

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        read_only = d.pop("readOnly", UNSET)

        value = d.pop("value", UNSET)

        name = d.pop("name", UNSET)

        _item_reference = d.pop("itemReference", UNSET)
        item_reference: ItemReferenceDto | Unset
        if isinstance(_item_reference, Unset) or _item_reference is None:
            item_reference = UNSET
        else:
            item_reference = ItemReferenceDto.from_dict(_item_reference)

        _item_characteristics = d.pop("itemCharacteristics", UNSET)
        item_characteristics: ItemCharacteristicsDto | Unset
        if isinstance(_item_characteristics, Unset) or _item_characteristics is None:
            item_characteristics = UNSET
        else:
            item_characteristics = ItemCharacteristicsDto.from_dict(_item_characteristics)

        _created = d.pop("created", UNSET)
        created: datetime.datetime | Unset
        if isinstance(_created, Unset) or _created is None:
            created = UNSET
        else:
            created = isoparse(_created)

        _modified = d.pop("modified", UNSET)
        modified: datetime.datetime | Unset
        if isinstance(_modified, Unset) or _modified is None:
            modified = UNSET
        else:
            modified = isoparse(_modified)

        _deleted = d.pop("deleted", UNSET)
        deleted: datetime.datetime | Unset
        if isinstance(_deleted, Unset) or _deleted is None:
            deleted = UNSET
        else:
            deleted = isoparse(_deleted)

        chargepoint_configuration_items_dto = cls(
            id=id,
            read_only=read_only,
            value=value,
            name=name,
            item_reference=item_reference,
            item_characteristics=item_characteristics,
            created=created,
            modified=modified,
            deleted=deleted,
        )

        chargepoint_configuration_items_dto.additional_properties = d
        return chargepoint_configuration_items_dto

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

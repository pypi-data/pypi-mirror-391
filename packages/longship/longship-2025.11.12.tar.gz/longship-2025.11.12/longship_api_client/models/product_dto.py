from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ProductDto")


@_attrs_define
class ProductDto:
    """
    Attributes:
        id (str):
        product_id (str):
        tenant_id (str):
        ou (str):
        created (datetime.datetime):
        valid_from (datetime.datetime):
        name (str | Unset):
        price (float | Unset):
        description (str | Unset):
        modified (datetime.datetime | Unset):
        deleted (datetime.datetime | Unset):
        valid_to (datetime.datetime | Unset):
    """

    id: str
    product_id: str
    tenant_id: str
    ou: str
    created: datetime.datetime
    valid_from: datetime.datetime
    name: str | Unset = UNSET
    price: float | Unset = UNSET
    description: str | Unset = UNSET
    modified: datetime.datetime | Unset = UNSET
    deleted: datetime.datetime | Unset = UNSET
    valid_to: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        product_id = self.product_id

        tenant_id = self.tenant_id

        ou = self.ou

        created = self.created.isoformat()

        valid_from = self.valid_from.isoformat()

        name = self.name

        price = self.price

        description = self.description

        modified: str | Unset = UNSET
        if not isinstance(self.modified, Unset):
            modified = self.modified.isoformat()

        deleted: str | Unset = UNSET
        if not isinstance(self.deleted, Unset):
            deleted = self.deleted.isoformat()

        valid_to: str | Unset = UNSET
        if not isinstance(self.valid_to, Unset):
            valid_to = self.valid_to.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "productId": product_id,
                "tenantId": tenant_id,
                "ou": ou,
                "created": created,
                "validFrom": valid_from,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if price is not UNSET:
            field_dict["price"] = price
        if description is not UNSET:
            field_dict["description"] = description
        if modified is not UNSET:
            field_dict["modified"] = modified
        if deleted is not UNSET:
            field_dict["deleted"] = deleted
        if valid_to is not UNSET:
            field_dict["validTo"] = valid_to

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        product_id = d.pop("productId")

        tenant_id = d.pop("tenantId")

        ou = d.pop("ou")

        created = isoparse(d.pop("created"))

        valid_from = isoparse(d.pop("validFrom"))

        name = d.pop("name", UNSET)

        price = d.pop("price", UNSET)

        description = d.pop("description", UNSET)

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

        _valid_to = d.pop("validTo", UNSET)
        valid_to: datetime.datetime | Unset
        if isinstance(_valid_to, Unset) or _valid_to is None:
            valid_to = UNSET
        else:
            valid_to = isoparse(_valid_to)

        product_dto = cls(
            id=id,
            product_id=product_id,
            tenant_id=tenant_id,
            ou=ou,
            created=created,
            valid_from=valid_from,
            name=name,
            price=price,
            description=description,
            modified=modified,
            deleted=deleted,
            valid_to=valid_to,
        )

        product_dto.additional_properties = d
        return product_dto

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

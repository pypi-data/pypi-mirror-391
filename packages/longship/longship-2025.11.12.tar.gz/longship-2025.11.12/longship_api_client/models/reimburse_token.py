from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReimburseToken")


@_attrs_define
class ReimburseToken:
    """
    Attributes:
        is_valid (bool):
        last_updated (datetime.datetime):
        contract_id (str | Unset):
        normalized_contract_id (str | Unset):
        token_uid (str | Unset):
        created_timestamp (datetime.datetime | Unset):
        valid_from (datetime.datetime | Unset):
    """

    is_valid: bool
    last_updated: datetime.datetime
    contract_id: str | Unset = UNSET
    normalized_contract_id: str | Unset = UNSET
    token_uid: str | Unset = UNSET
    created_timestamp: datetime.datetime | Unset = UNSET
    valid_from: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        is_valid = self.is_valid

        last_updated = self.last_updated.isoformat()

        contract_id = self.contract_id

        normalized_contract_id = self.normalized_contract_id

        token_uid = self.token_uid

        created_timestamp: str | Unset = UNSET
        if not isinstance(self.created_timestamp, Unset):
            created_timestamp = self.created_timestamp.isoformat()

        valid_from: str | Unset = UNSET
        if not isinstance(self.valid_from, Unset):
            valid_from = self.valid_from.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "isValid": is_valid,
                "lastUpdated": last_updated,
            }
        )
        if contract_id is not UNSET:
            field_dict["contractId"] = contract_id
        if normalized_contract_id is not UNSET:
            field_dict["normalizedContractId"] = normalized_contract_id
        if token_uid is not UNSET:
            field_dict["TokenUid"] = token_uid
        if created_timestamp is not UNSET:
            field_dict["createdTimestamp"] = created_timestamp
        if valid_from is not UNSET:
            field_dict["validFrom"] = valid_from

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        is_valid = d.pop("isValid")

        last_updated = isoparse(d.pop("lastUpdated"))

        contract_id = d.pop("contractId", UNSET)

        normalized_contract_id = d.pop("normalizedContractId", UNSET)

        token_uid = d.pop("TokenUid", UNSET)

        _created_timestamp = d.pop("createdTimestamp", UNSET)
        created_timestamp: datetime.datetime | Unset
        if isinstance(_created_timestamp, Unset) or _created_timestamp is None:
            created_timestamp = UNSET
        else:
            created_timestamp = isoparse(_created_timestamp)

        _valid_from = d.pop("validFrom", UNSET)
        valid_from: datetime.datetime | Unset
        if isinstance(_valid_from, Unset) or _valid_from is None:
            valid_from = UNSET
        else:
            valid_from = isoparse(_valid_from)

        reimburse_token = cls(
            is_valid=is_valid,
            last_updated=last_updated,
            contract_id=contract_id,
            normalized_contract_id=normalized_contract_id,
            token_uid=token_uid,
            created_timestamp=created_timestamp,
            valid_from=valid_from,
        )

        reimburse_token.additional_properties = d
        return reimburse_token

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

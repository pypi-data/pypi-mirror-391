from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReimbursementBankDetailsDto")


@_attrs_define
class ReimbursementBankDetailsDto:
    """
    Attributes:
        bankaccount (str | Unset):
        date_created (datetime.datetime | Unset):
        valid_from (datetime.datetime | Unset):
    """

    bankaccount: str | Unset = UNSET
    date_created: datetime.datetime | Unset = UNSET
    valid_from: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bankaccount = self.bankaccount

        date_created: str | Unset = UNSET
        if not isinstance(self.date_created, Unset):
            date_created = self.date_created.isoformat()

        valid_from: str | Unset = UNSET
        if not isinstance(self.valid_from, Unset):
            valid_from = self.valid_from.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if bankaccount is not UNSET:
            field_dict["bankaccount"] = bankaccount
        if date_created is not UNSET:
            field_dict["dateCreated"] = date_created
        if valid_from is not UNSET:
            field_dict["validFrom"] = valid_from

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        bankaccount = d.pop("bankaccount", UNSET)

        _date_created = d.pop("dateCreated", UNSET)
        date_created: datetime.datetime | Unset
        if isinstance(_date_created, Unset) or _date_created is None:
            date_created = UNSET
        else:
            date_created = isoparse(_date_created)

        _valid_from = d.pop("validFrom", UNSET)
        valid_from: datetime.datetime | Unset
        if isinstance(_valid_from, Unset) or _valid_from is None:
            valid_from = UNSET
        else:
            valid_from = isoparse(_valid_from)

        reimbursement_bank_details_dto = cls(
            bankaccount=bankaccount,
            date_created=date_created,
            valid_from=valid_from,
        )

        reimbursement_bank_details_dto.additional_properties = d
        return reimbursement_bank_details_dto

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

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.cdr_patch_dto_approval_status import CdrPatchDtoApprovalStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="CdrPatchDto")


@_attrs_define
class CdrPatchDto:
    """
    Attributes:
        approval_status (CdrPatchDtoApprovalStatus | Unset):  Default: CdrPatchDtoApprovalStatus.APPROVED.
    """

    approval_status: CdrPatchDtoApprovalStatus | Unset = CdrPatchDtoApprovalStatus.APPROVED
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        approval_status: str | Unset = UNSET
        if not isinstance(self.approval_status, Unset):
            approval_status = self.approval_status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if approval_status is not UNSET:
            field_dict["approvalStatus"] = approval_status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _approval_status = d.pop("approvalStatus", UNSET)
        approval_status: CdrPatchDtoApprovalStatus | Unset
        if isinstance(_approval_status, Unset) or _approval_status is None:
            approval_status = UNSET
        else:
            approval_status = CdrPatchDtoApprovalStatus(_approval_status)

        cdr_patch_dto = cls(
            approval_status=approval_status,
        )

        cdr_patch_dto.additional_properties = d
        return cdr_patch_dto

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

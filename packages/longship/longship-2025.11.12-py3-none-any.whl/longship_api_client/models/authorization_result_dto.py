from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.authorization_result_dto_reason import AuthorizationResultDtoReason
from ..models.authorization_result_dto_status import AuthorizationResultDtoStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.authorization_assertion_dto import AuthorizationAssertionDto


T = TypeVar("T", bound="AuthorizationResultDto")


@_attrs_define
class AuthorizationResultDto:
    """
    Attributes:
        assertion (list[AuthorizationAssertionDto] | Unset):
        status (AuthorizationResultDtoStatus | Unset):  Default: AuthorizationResultDtoStatus.ACCEPTED.
        reason (AuthorizationResultDtoReason | Unset):  Default: AuthorizationResultDtoReason.APPROVEDBYREMOTE.
        description (str | Unset):
    """

    assertion: list[AuthorizationAssertionDto] | Unset = UNSET
    status: AuthorizationResultDtoStatus | Unset = AuthorizationResultDtoStatus.ACCEPTED
    reason: AuthorizationResultDtoReason | Unset = AuthorizationResultDtoReason.APPROVEDBYREMOTE
    description: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        assertion: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.assertion, Unset):
            assertion = []
            for assertion_item_data in self.assertion:
                assertion_item = assertion_item_data.to_dict()
                assertion.append(assertion_item)

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        reason: str | Unset = UNSET
        if not isinstance(self.reason, Unset):
            reason = self.reason.value

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if assertion is not UNSET:
            field_dict["assertion"] = assertion
        if status is not UNSET:
            field_dict["status"] = status
        if reason is not UNSET:
            field_dict["reason"] = reason
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.authorization_assertion_dto import AuthorizationAssertionDto

        d = dict(src_dict)
        assertion = []
        _assertion = d.pop("assertion", UNSET)
        for assertion_item_data in _assertion or []:
            assertion_item = AuthorizationAssertionDto.from_dict(assertion_item_data)

            assertion.append(assertion_item)

        _status = d.pop("status", UNSET)
        status: AuthorizationResultDtoStatus | Unset
        if isinstance(_status, Unset) or _status is None:
            status = UNSET
        else:
            status = AuthorizationResultDtoStatus(_status)

        _reason = d.pop("reason", UNSET)
        reason: AuthorizationResultDtoReason | Unset
        if isinstance(_reason, Unset) or _reason is None:
            reason = UNSET
        else:
            reason = AuthorizationResultDtoReason(_reason)

        description = d.pop("description", UNSET)

        authorization_result_dto = cls(
            assertion=assertion,
            status=status,
            reason=reason,
            description=description,
        )

        authorization_result_dto.additional_properties = d
        return authorization_result_dto

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

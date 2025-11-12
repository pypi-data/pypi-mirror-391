from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.longship_error_detail import LongshipErrorDetail


T = TypeVar("T", bound="LongshipError")


@_attrs_define
class LongshipError:
    """
    Attributes:
        code (str | Unset): The error code.
        error_details (LongshipErrorDetail | Unset): More details about the error.
    """

    code: str | Unset = UNSET
    error_details: LongshipErrorDetail | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        code = self.code

        error_details: dict[str, Any] | Unset = UNSET
        if not isinstance(self.error_details, Unset):
            error_details = self.error_details.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if code is not UNSET:
            field_dict["code"] = code
        if error_details is not UNSET:
            field_dict["errorDetails"] = error_details

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.longship_error_detail import LongshipErrorDetail

        d = dict(src_dict)
        code = d.pop("code", UNSET)

        _error_details = d.pop("errorDetails", UNSET)
        error_details: LongshipErrorDetail | Unset
        if isinstance(_error_details, Unset) or _error_details is None:
            error_details = UNSET
        else:
            error_details = LongshipErrorDetail.from_dict(_error_details)

        longship_error = cls(
            code=code,
            error_details=error_details,
        )

        longship_error.additional_properties = d
        return longship_error

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

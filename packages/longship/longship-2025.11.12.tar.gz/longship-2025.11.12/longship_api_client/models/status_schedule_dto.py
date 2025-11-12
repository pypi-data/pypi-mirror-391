from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.status_schedule_dto_status import StatusScheduleDtoStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="StatusScheduleDto")


@_attrs_define
class StatusScheduleDto:
    """
    Attributes:
        period_begin (datetime.datetime | Unset):
        period_end (datetime.datetime | Unset):
        status (StatusScheduleDtoStatus | Unset):  Default: StatusScheduleDtoStatus.AVAILABLE.
    """

    period_begin: datetime.datetime | Unset = UNSET
    period_end: datetime.datetime | Unset = UNSET
    status: StatusScheduleDtoStatus | Unset = StatusScheduleDtoStatus.AVAILABLE
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        period_begin: str | Unset = UNSET
        if not isinstance(self.period_begin, Unset):
            period_begin = self.period_begin.isoformat()

        period_end: str | Unset = UNSET
        if not isinstance(self.period_end, Unset):
            period_end = self.period_end.isoformat()

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if period_begin is not UNSET:
            field_dict["period_begin"] = period_begin
        if period_end is not UNSET:
            field_dict["period_end"] = period_end
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _period_begin = d.pop("period_begin", UNSET)
        period_begin: datetime.datetime | Unset
        if isinstance(_period_begin, Unset) or _period_begin is None:
            period_begin = UNSET
        else:
            period_begin = isoparse(_period_begin)

        _period_end = d.pop("period_end", UNSET)
        period_end: datetime.datetime | Unset
        if isinstance(_period_end, Unset) or _period_end is None:
            period_end = UNSET
        else:
            period_end = isoparse(_period_end)

        _status = d.pop("status", UNSET)
        status: StatusScheduleDtoStatus | Unset
        if isinstance(_status, Unset) or _status is None:
            status = UNSET
        else:
            status = StatusScheduleDtoStatus(_status)

        status_schedule_dto = cls(
            period_begin=period_begin,
            period_end=period_end,
            status=status,
        )

        status_schedule_dto.additional_properties = d
        return status_schedule_dto

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

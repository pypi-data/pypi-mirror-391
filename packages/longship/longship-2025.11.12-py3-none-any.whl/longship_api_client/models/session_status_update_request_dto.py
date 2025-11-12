from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.session_status_update_request_dto_status import SessionStatusUpdateRequestDtoStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="SessionStatusUpdateRequestDto")


@_attrs_define
class SessionStatusUpdateRequestDto:
    """
    Attributes:
        status (SessionStatusUpdateRequestDtoStatus | Unset):  Default: SessionStatusUpdateRequestDtoStatus.ACTIVE.
        meter_stop_in_wh (int | Unset):
        session_stop (datetime.datetime | Unset):
    """

    status: SessionStatusUpdateRequestDtoStatus | Unset = SessionStatusUpdateRequestDtoStatus.ACTIVE
    meter_stop_in_wh: int | Unset = UNSET
    session_stop: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        meter_stop_in_wh = self.meter_stop_in_wh

        session_stop: str | Unset = UNSET
        if not isinstance(self.session_stop, Unset):
            session_stop = self.session_stop.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if status is not UNSET:
            field_dict["status"] = status
        if meter_stop_in_wh is not UNSET:
            field_dict["meterStopInWh"] = meter_stop_in_wh
        if session_stop is not UNSET:
            field_dict["sessionStop"] = session_stop

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _status = d.pop("status", UNSET)
        status: SessionStatusUpdateRequestDtoStatus | Unset
        if isinstance(_status, Unset) or _status is None:
            status = UNSET
        else:
            status = SessionStatusUpdateRequestDtoStatus(_status)

        meter_stop_in_wh = d.pop("meterStopInWh", UNSET)

        _session_stop = d.pop("sessionStop", UNSET)
        session_stop: datetime.datetime | Unset
        if isinstance(_session_stop, Unset) or _session_stop is None:
            session_stop = UNSET
        else:
            session_stop = isoparse(_session_stop)

        session_status_update_request_dto = cls(
            status=status,
            meter_stop_in_wh=meter_stop_in_wh,
            session_stop=session_stop,
        )

        session_status_update_request_dto.additional_properties = d
        return session_status_update_request_dto

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

from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetDiagnosticsRequest")


@_attrs_define
class GetDiagnosticsRequest:
    """
    Attributes:
        location (str):
        retries (int | Unset):
        retry_interval (int | Unset):
        start_time (datetime.datetime | Unset):
        stop_time (datetime.datetime | Unset):
    """

    location: str
    retries: int | Unset = UNSET
    retry_interval: int | Unset = UNSET
    start_time: datetime.datetime | Unset = UNSET
    stop_time: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        location = self.location

        retries = self.retries

        retry_interval = self.retry_interval

        start_time: str | Unset = UNSET
        if not isinstance(self.start_time, Unset):
            start_time = self.start_time.isoformat()

        stop_time: str | Unset = UNSET
        if not isinstance(self.stop_time, Unset):
            stop_time = self.stop_time.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "location": location,
            }
        )
        if retries is not UNSET:
            field_dict["retries"] = retries
        if retry_interval is not UNSET:
            field_dict["retryInterval"] = retry_interval
        if start_time is not UNSET:
            field_dict["startTime"] = start_time
        if stop_time is not UNSET:
            field_dict["stopTime"] = stop_time

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        location = d.pop("location")

        retries = d.pop("retries", UNSET)

        retry_interval = d.pop("retryInterval", UNSET)

        _start_time = d.pop("startTime", UNSET)
        start_time: datetime.datetime | Unset
        if isinstance(_start_time, Unset) or _start_time is None:
            start_time = UNSET
        else:
            start_time = isoparse(_start_time)

        _stop_time = d.pop("stopTime", UNSET)
        stop_time: datetime.datetime | Unset
        if isinstance(_stop_time, Unset) or _stop_time is None:
            stop_time = UNSET
        else:
            stop_time = isoparse(_stop_time)

        get_diagnostics_request = cls(
            location=location,
            retries=retries,
            retry_interval=retry_interval,
            start_time=start_time,
            stop_time=stop_time,
        )

        get_diagnostics_request.additional_properties = d
        return get_diagnostics_request

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

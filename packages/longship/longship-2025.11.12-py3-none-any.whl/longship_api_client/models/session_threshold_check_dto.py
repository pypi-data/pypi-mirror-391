from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.session_threshold_check_dto_status import SessionThresholdCheckDtoStatus
from ..models.session_threshold_check_dto_threshold_hit_outcome import SessionThresholdCheckDtoThresholdHitOutcome
from ..types import UNSET, Unset

T = TypeVar("T", bound="SessionThresholdCheckDto")


@_attrs_define
class SessionThresholdCheckDto:
    """
    Attributes:
        threshold_hit_outcome (SessionThresholdCheckDtoThresholdHitOutcome | Unset):  Default:
            SessionThresholdCheckDtoThresholdHitOutcome.SUSPICIOUS.
        status (SessionThresholdCheckDtoStatus | Unset):  Default: SessionThresholdCheckDtoStatus.PENDING.
        result (str | Unset):
        is_enabled (bool | Unset):
    """

    threshold_hit_outcome: SessionThresholdCheckDtoThresholdHitOutcome | Unset = (
        SessionThresholdCheckDtoThresholdHitOutcome.SUSPICIOUS
    )
    status: SessionThresholdCheckDtoStatus | Unset = SessionThresholdCheckDtoStatus.PENDING
    result: str | Unset = UNSET
    is_enabled: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        threshold_hit_outcome: str | Unset = UNSET
        if not isinstance(self.threshold_hit_outcome, Unset):
            threshold_hit_outcome = self.threshold_hit_outcome.value

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        result = self.result

        is_enabled = self.is_enabled

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if threshold_hit_outcome is not UNSET:
            field_dict["thresholdHitOutcome"] = threshold_hit_outcome
        if status is not UNSET:
            field_dict["status"] = status
        if result is not UNSET:
            field_dict["result"] = result
        if is_enabled is not UNSET:
            field_dict["isEnabled"] = is_enabled

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _threshold_hit_outcome = d.pop("thresholdHitOutcome", UNSET)
        threshold_hit_outcome: SessionThresholdCheckDtoThresholdHitOutcome | Unset
        if isinstance(_threshold_hit_outcome, Unset) or _threshold_hit_outcome is None:
            threshold_hit_outcome = UNSET
        else:
            threshold_hit_outcome = SessionThresholdCheckDtoThresholdHitOutcome(_threshold_hit_outcome)

        _status = d.pop("status", UNSET)
        status: SessionThresholdCheckDtoStatus | Unset
        if isinstance(_status, Unset) or _status is None:
            status = UNSET
        else:
            status = SessionThresholdCheckDtoStatus(_status)

        result = d.pop("result", UNSET)

        is_enabled = d.pop("isEnabled", UNSET)

        session_threshold_check_dto = cls(
            threshold_hit_outcome=threshold_hit_outcome,
            status=status,
            result=result,
            is_enabled=is_enabled,
        )

        session_threshold_check_dto.additional_properties = d
        return session_threshold_check_dto

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

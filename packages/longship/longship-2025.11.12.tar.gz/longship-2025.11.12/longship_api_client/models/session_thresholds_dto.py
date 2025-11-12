from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.session_thresholds_dto_thresholds_hit_item import SessionThresholdsDtoThresholdsHitItem
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.session_threshold_check_dto import SessionThresholdCheckDto
    from ..models.session_threshold_value_dto_decimal import SessionThresholdValueDtoDecimal
    from ..models.session_threshold_value_dto_int_32 import SessionThresholdValueDtoInt32


T = TypeVar("T", bound="SessionThresholdsDto")


@_attrs_define
class SessionThresholdsDto:
    """
    Attributes:
        thresholds_hit (list[SessionThresholdsDtoThresholdsHitItem] | Unset):
        min_kwh_ac (SessionThresholdValueDtoDecimal | Unset):
        max_kwh_ac (SessionThresholdValueDtoDecimal | Unset):
        min_kwh_dc (SessionThresholdValueDtoDecimal | Unset):
        max_kwh_dc (SessionThresholdValueDtoDecimal | Unset):
        min_duration_in_minutes_ac (SessionThresholdValueDtoInt32 | Unset):
        min_duration_in_minutes_dc (SessionThresholdValueDtoInt32 | Unset):
        max_session_age_in_days (SessionThresholdValueDtoInt32 | Unset):
        check_charging_speed (SessionThresholdCheckDto | Unset):
        check_session_in_future (SessionThresholdCheckDto | Unset):
    """

    thresholds_hit: list[SessionThresholdsDtoThresholdsHitItem] | Unset = UNSET
    min_kwh_ac: SessionThresholdValueDtoDecimal | Unset = UNSET
    max_kwh_ac: SessionThresholdValueDtoDecimal | Unset = UNSET
    min_kwh_dc: SessionThresholdValueDtoDecimal | Unset = UNSET
    max_kwh_dc: SessionThresholdValueDtoDecimal | Unset = UNSET
    min_duration_in_minutes_ac: SessionThresholdValueDtoInt32 | Unset = UNSET
    min_duration_in_minutes_dc: SessionThresholdValueDtoInt32 | Unset = UNSET
    max_session_age_in_days: SessionThresholdValueDtoInt32 | Unset = UNSET
    check_charging_speed: SessionThresholdCheckDto | Unset = UNSET
    check_session_in_future: SessionThresholdCheckDto | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        thresholds_hit: list[str] | Unset = UNSET
        if not isinstance(self.thresholds_hit, Unset):
            thresholds_hit = []
            for thresholds_hit_item_data in self.thresholds_hit:
                thresholds_hit_item = thresholds_hit_item_data.value
                thresholds_hit.append(thresholds_hit_item)

        min_kwh_ac: dict[str, Any] | Unset = UNSET
        if not isinstance(self.min_kwh_ac, Unset):
            min_kwh_ac = self.min_kwh_ac.to_dict()

        max_kwh_ac: dict[str, Any] | Unset = UNSET
        if not isinstance(self.max_kwh_ac, Unset):
            max_kwh_ac = self.max_kwh_ac.to_dict()

        min_kwh_dc: dict[str, Any] | Unset = UNSET
        if not isinstance(self.min_kwh_dc, Unset):
            min_kwh_dc = self.min_kwh_dc.to_dict()

        max_kwh_dc: dict[str, Any] | Unset = UNSET
        if not isinstance(self.max_kwh_dc, Unset):
            max_kwh_dc = self.max_kwh_dc.to_dict()

        min_duration_in_minutes_ac: dict[str, Any] | Unset = UNSET
        if not isinstance(self.min_duration_in_minutes_ac, Unset):
            min_duration_in_minutes_ac = self.min_duration_in_minutes_ac.to_dict()

        min_duration_in_minutes_dc: dict[str, Any] | Unset = UNSET
        if not isinstance(self.min_duration_in_minutes_dc, Unset):
            min_duration_in_minutes_dc = self.min_duration_in_minutes_dc.to_dict()

        max_session_age_in_days: dict[str, Any] | Unset = UNSET
        if not isinstance(self.max_session_age_in_days, Unset):
            max_session_age_in_days = self.max_session_age_in_days.to_dict()

        check_charging_speed: dict[str, Any] | Unset = UNSET
        if not isinstance(self.check_charging_speed, Unset):
            check_charging_speed = self.check_charging_speed.to_dict()

        check_session_in_future: dict[str, Any] | Unset = UNSET
        if not isinstance(self.check_session_in_future, Unset):
            check_session_in_future = self.check_session_in_future.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if thresholds_hit is not UNSET:
            field_dict["thresholdsHit"] = thresholds_hit
        if min_kwh_ac is not UNSET:
            field_dict["minKwhAc"] = min_kwh_ac
        if max_kwh_ac is not UNSET:
            field_dict["maxKwhAc"] = max_kwh_ac
        if min_kwh_dc is not UNSET:
            field_dict["minKwhDc"] = min_kwh_dc
        if max_kwh_dc is not UNSET:
            field_dict["maxKwhDc"] = max_kwh_dc
        if min_duration_in_minutes_ac is not UNSET:
            field_dict["minDurationInMinutesAc"] = min_duration_in_minutes_ac
        if min_duration_in_minutes_dc is not UNSET:
            field_dict["minDurationInMinutesDc"] = min_duration_in_minutes_dc
        if max_session_age_in_days is not UNSET:
            field_dict["maxSessionAgeInDays"] = max_session_age_in_days
        if check_charging_speed is not UNSET:
            field_dict["checkChargingSpeed"] = check_charging_speed
        if check_session_in_future is not UNSET:
            field_dict["checkSessionInFuture"] = check_session_in_future

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.session_threshold_check_dto import SessionThresholdCheckDto
        from ..models.session_threshold_value_dto_decimal import SessionThresholdValueDtoDecimal
        from ..models.session_threshold_value_dto_int_32 import SessionThresholdValueDtoInt32

        d = dict(src_dict)
        thresholds_hit = []
        _thresholds_hit = d.pop("thresholdsHit", UNSET)
        for thresholds_hit_item_data in _thresholds_hit or []:
            thresholds_hit_item = SessionThresholdsDtoThresholdsHitItem(thresholds_hit_item_data)

            thresholds_hit.append(thresholds_hit_item)

        _min_kwh_ac = d.pop("minKwhAc", UNSET)
        min_kwh_ac: SessionThresholdValueDtoDecimal | Unset
        if isinstance(_min_kwh_ac, Unset) or _min_kwh_ac is None:
            min_kwh_ac = UNSET
        else:
            min_kwh_ac = SessionThresholdValueDtoDecimal.from_dict(_min_kwh_ac)

        _max_kwh_ac = d.pop("maxKwhAc", UNSET)
        max_kwh_ac: SessionThresholdValueDtoDecimal | Unset
        if isinstance(_max_kwh_ac, Unset) or _max_kwh_ac is None:
            max_kwh_ac = UNSET
        else:
            max_kwh_ac = SessionThresholdValueDtoDecimal.from_dict(_max_kwh_ac)

        _min_kwh_dc = d.pop("minKwhDc", UNSET)
        min_kwh_dc: SessionThresholdValueDtoDecimal | Unset
        if isinstance(_min_kwh_dc, Unset) or _min_kwh_dc is None:
            min_kwh_dc = UNSET
        else:
            min_kwh_dc = SessionThresholdValueDtoDecimal.from_dict(_min_kwh_dc)

        _max_kwh_dc = d.pop("maxKwhDc", UNSET)
        max_kwh_dc: SessionThresholdValueDtoDecimal | Unset
        if isinstance(_max_kwh_dc, Unset) or _max_kwh_dc is None:
            max_kwh_dc = UNSET
        else:
            max_kwh_dc = SessionThresholdValueDtoDecimal.from_dict(_max_kwh_dc)

        _min_duration_in_minutes_ac = d.pop("minDurationInMinutesAc", UNSET)
        min_duration_in_minutes_ac: SessionThresholdValueDtoInt32 | Unset
        if isinstance(_min_duration_in_minutes_ac, Unset) or _min_duration_in_minutes_ac is None:
            min_duration_in_minutes_ac = UNSET
        else:
            min_duration_in_minutes_ac = SessionThresholdValueDtoInt32.from_dict(_min_duration_in_minutes_ac)

        _min_duration_in_minutes_dc = d.pop("minDurationInMinutesDc", UNSET)
        min_duration_in_minutes_dc: SessionThresholdValueDtoInt32 | Unset
        if isinstance(_min_duration_in_minutes_dc, Unset) or _min_duration_in_minutes_dc is None:
            min_duration_in_minutes_dc = UNSET
        else:
            min_duration_in_minutes_dc = SessionThresholdValueDtoInt32.from_dict(_min_duration_in_minutes_dc)

        _max_session_age_in_days = d.pop("maxSessionAgeInDays", UNSET)
        max_session_age_in_days: SessionThresholdValueDtoInt32 | Unset
        if isinstance(_max_session_age_in_days, Unset) or _max_session_age_in_days is None:
            max_session_age_in_days = UNSET
        else:
            max_session_age_in_days = SessionThresholdValueDtoInt32.from_dict(_max_session_age_in_days)

        _check_charging_speed = d.pop("checkChargingSpeed", UNSET)
        check_charging_speed: SessionThresholdCheckDto | Unset
        if isinstance(_check_charging_speed, Unset) or _check_charging_speed is None:
            check_charging_speed = UNSET
        else:
            check_charging_speed = SessionThresholdCheckDto.from_dict(_check_charging_speed)

        _check_session_in_future = d.pop("checkSessionInFuture", UNSET)
        check_session_in_future: SessionThresholdCheckDto | Unset
        if isinstance(_check_session_in_future, Unset) or _check_session_in_future is None:
            check_session_in_future = UNSET
        else:
            check_session_in_future = SessionThresholdCheckDto.from_dict(_check_session_in_future)

        session_thresholds_dto = cls(
            thresholds_hit=thresholds_hit,
            min_kwh_ac=min_kwh_ac,
            max_kwh_ac=max_kwh_ac,
            min_kwh_dc=min_kwh_dc,
            max_kwh_dc=max_kwh_dc,
            min_duration_in_minutes_ac=min_duration_in_minutes_ac,
            min_duration_in_minutes_dc=min_duration_in_minutes_dc,
            max_session_age_in_days=max_session_age_in_days,
            check_charging_speed=check_charging_speed,
            check_session_in_future=check_session_in_future,
        )

        session_thresholds_dto.additional_properties = d
        return session_thresholds_dto

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

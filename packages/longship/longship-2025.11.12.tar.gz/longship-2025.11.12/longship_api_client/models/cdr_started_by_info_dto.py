from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.cdr_started_by_info_dto_authorization_state import CdrStartedByInfoDtoAuthorizationState
from ..models.cdr_started_by_info_dto_roaming_platform_type import CdrStartedByInfoDtoRoamingPlatformType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cdr_started_by_token_dto import CdrStartedByTokenDto


T = TypeVar("T", bound="CdrStartedByInfoDto")


@_attrs_define
class CdrStartedByInfoDto:
    """
    Attributes:
        token_info (CdrStartedByTokenDto | Unset):
        roaming_platform_type (CdrStartedByInfoDtoRoamingPlatformType | Unset):  Default:
            CdrStartedByInfoDtoRoamingPlatformType.HUBJECT.
        authorization_state (CdrStartedByInfoDtoAuthorizationState | Unset):  Default:
            CdrStartedByInfoDtoAuthorizationState.APPROVEDBYREMOTE.
        roaming_platform_connection_id (str | Unset):
        is_guest_usage (bool | Unset):
    """

    token_info: CdrStartedByTokenDto | Unset = UNSET
    roaming_platform_type: CdrStartedByInfoDtoRoamingPlatformType | Unset = (
        CdrStartedByInfoDtoRoamingPlatformType.HUBJECT
    )
    authorization_state: CdrStartedByInfoDtoAuthorizationState | Unset = (
        CdrStartedByInfoDtoAuthorizationState.APPROVEDBYREMOTE
    )
    roaming_platform_connection_id: str | Unset = UNSET
    is_guest_usage: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        token_info: dict[str, Any] | Unset = UNSET
        if not isinstance(self.token_info, Unset):
            token_info = self.token_info.to_dict()

        roaming_platform_type: str | Unset = UNSET
        if not isinstance(self.roaming_platform_type, Unset):
            roaming_platform_type = self.roaming_platform_type.value

        authorization_state: str | Unset = UNSET
        if not isinstance(self.authorization_state, Unset):
            authorization_state = self.authorization_state.value

        roaming_platform_connection_id = self.roaming_platform_connection_id

        is_guest_usage = self.is_guest_usage

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if token_info is not UNSET:
            field_dict["tokenInfo"] = token_info
        if roaming_platform_type is not UNSET:
            field_dict["roamingPlatformType"] = roaming_platform_type
        if authorization_state is not UNSET:
            field_dict["authorizationState"] = authorization_state
        if roaming_platform_connection_id is not UNSET:
            field_dict["roamingPlatformConnectionId"] = roaming_platform_connection_id
        if is_guest_usage is not UNSET:
            field_dict["isGuestUsage"] = is_guest_usage

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cdr_started_by_token_dto import CdrStartedByTokenDto

        d = dict(src_dict)
        _token_info = d.pop("tokenInfo", UNSET)
        token_info: CdrStartedByTokenDto | Unset
        if isinstance(_token_info, Unset) or _token_info is None:
            token_info = UNSET
        else:
            token_info = CdrStartedByTokenDto.from_dict(_token_info)

        _roaming_platform_type = d.pop("roamingPlatformType", UNSET)
        roaming_platform_type: CdrStartedByInfoDtoRoamingPlatformType | Unset
        if isinstance(_roaming_platform_type, Unset) or _roaming_platform_type is None:
            roaming_platform_type = UNSET
        else:
            roaming_platform_type = CdrStartedByInfoDtoRoamingPlatformType(_roaming_platform_type)

        _authorization_state = d.pop("authorizationState", UNSET)
        authorization_state: CdrStartedByInfoDtoAuthorizationState | Unset
        if isinstance(_authorization_state, Unset) or _authorization_state is None:
            authorization_state = UNSET
        else:
            authorization_state = CdrStartedByInfoDtoAuthorizationState(_authorization_state)

        roaming_platform_connection_id = d.pop("roamingPlatformConnectionId", UNSET)

        is_guest_usage = d.pop("isGuestUsage", UNSET)

        cdr_started_by_info_dto = cls(
            token_info=token_info,
            roaming_platform_type=roaming_platform_type,
            authorization_state=authorization_state,
            roaming_platform_connection_id=roaming_platform_connection_id,
            is_guest_usage=is_guest_usage,
        )

        cdr_started_by_info_dto.additional_properties = d
        return cdr_started_by_info_dto

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

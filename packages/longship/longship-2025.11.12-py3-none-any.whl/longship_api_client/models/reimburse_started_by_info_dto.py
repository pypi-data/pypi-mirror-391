from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.reimburse_started_by_info_dto_authorization_state import ReimburseStartedByInfoDtoAuthorizationState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.reimburse_started_by_token_dto import ReimburseStartedByTokenDto


T = TypeVar("T", bound="ReimburseStartedByInfoDto")


@_attrs_define
class ReimburseStartedByInfoDto:
    """
    Attributes:
        id_tag (str | Unset):
        token_info (ReimburseStartedByTokenDto | Unset):
        authorization_state (ReimburseStartedByInfoDtoAuthorizationState | Unset):  Default:
            ReimburseStartedByInfoDtoAuthorizationState.APPROVEDBYREMOTE.
        is_guest_usage (bool | Unset):
    """

    id_tag: str | Unset = UNSET
    token_info: ReimburseStartedByTokenDto | Unset = UNSET
    authorization_state: ReimburseStartedByInfoDtoAuthorizationState | Unset = (
        ReimburseStartedByInfoDtoAuthorizationState.APPROVEDBYREMOTE
    )
    is_guest_usage: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id_tag = self.id_tag

        token_info: dict[str, Any] | Unset = UNSET
        if not isinstance(self.token_info, Unset):
            token_info = self.token_info.to_dict()

        authorization_state: str | Unset = UNSET
        if not isinstance(self.authorization_state, Unset):
            authorization_state = self.authorization_state.value

        is_guest_usage = self.is_guest_usage

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id_tag is not UNSET:
            field_dict["idTag"] = id_tag
        if token_info is not UNSET:
            field_dict["tokenInfo"] = token_info
        if authorization_state is not UNSET:
            field_dict["authorizationState"] = authorization_state
        if is_guest_usage is not UNSET:
            field_dict["isGuestUsage"] = is_guest_usage

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.reimburse_started_by_token_dto import ReimburseStartedByTokenDto

        d = dict(src_dict)
        id_tag = d.pop("idTag", UNSET)

        _token_info = d.pop("tokenInfo", UNSET)
        token_info: ReimburseStartedByTokenDto | Unset
        if isinstance(_token_info, Unset) or _token_info is None:
            token_info = UNSET
        else:
            token_info = ReimburseStartedByTokenDto.from_dict(_token_info)

        _authorization_state = d.pop("authorizationState", UNSET)
        authorization_state: ReimburseStartedByInfoDtoAuthorizationState | Unset
        if isinstance(_authorization_state, Unset) or _authorization_state is None:
            authorization_state = UNSET
        else:
            authorization_state = ReimburseStartedByInfoDtoAuthorizationState(_authorization_state)

        is_guest_usage = d.pop("isGuestUsage", UNSET)

        reimburse_started_by_info_dto = cls(
            id_tag=id_tag,
            token_info=token_info,
            authorization_state=authorization_state,
            is_guest_usage=is_guest_usage,
        )

        reimburse_started_by_info_dto.additional_properties = d
        return reimburse_started_by_info_dto

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

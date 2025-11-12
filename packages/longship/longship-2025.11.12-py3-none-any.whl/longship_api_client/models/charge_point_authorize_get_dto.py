from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.charge_point_authorize_get_dto_authorization_request_type import (
    ChargePointAuthorizeGetDtoAuthorizationRequestType,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.authorization_context_details_dto import AuthorizationContextDetailsDto
    from ..models.authorization_result_dto import AuthorizationResultDto
    from ..models.token_info_dto import TokenInfoDto


T = TypeVar("T", bound="ChargePointAuthorizeGetDto")


@_attrs_define
class ChargePointAuthorizeGetDto:
    """
    Attributes:
        id (str | Unset):
        message_id (str | Unset):
        created (datetime.datetime | Unset):
        token_info (TokenInfoDto | Unset):
        authorization_request_type (ChargePointAuthorizeGetDtoAuthorizationRequestType | Unset):  Default:
            ChargePointAuthorizeGetDtoAuthorizationRequestType.AUTHORIZE.
        authorization_result (AuthorizationResultDto | Unset):
        context (AuthorizationContextDetailsDto | Unset):
    """

    id: str | Unset = UNSET
    message_id: str | Unset = UNSET
    created: datetime.datetime | Unset = UNSET
    token_info: TokenInfoDto | Unset = UNSET
    authorization_request_type: ChargePointAuthorizeGetDtoAuthorizationRequestType | Unset = (
        ChargePointAuthorizeGetDtoAuthorizationRequestType.AUTHORIZE
    )
    authorization_result: AuthorizationResultDto | Unset = UNSET
    context: AuthorizationContextDetailsDto | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        message_id = self.message_id

        created: str | Unset = UNSET
        if not isinstance(self.created, Unset):
            created = self.created.isoformat()

        token_info: dict[str, Any] | Unset = UNSET
        if not isinstance(self.token_info, Unset):
            token_info = self.token_info.to_dict()

        authorization_request_type: str | Unset = UNSET
        if not isinstance(self.authorization_request_type, Unset):
            authorization_request_type = self.authorization_request_type.value

        authorization_result: dict[str, Any] | Unset = UNSET
        if not isinstance(self.authorization_result, Unset):
            authorization_result = self.authorization_result.to_dict()

        context: dict[str, Any] | Unset = UNSET
        if not isinstance(self.context, Unset):
            context = self.context.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if message_id is not UNSET:
            field_dict["messageId"] = message_id
        if created is not UNSET:
            field_dict["created"] = created
        if token_info is not UNSET:
            field_dict["tokenInfo"] = token_info
        if authorization_request_type is not UNSET:
            field_dict["authorizationRequestType"] = authorization_request_type
        if authorization_result is not UNSET:
            field_dict["authorizationResult"] = authorization_result
        if context is not UNSET:
            field_dict["context"] = context

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.authorization_context_details_dto import AuthorizationContextDetailsDto
        from ..models.authorization_result_dto import AuthorizationResultDto
        from ..models.token_info_dto import TokenInfoDto

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        message_id = d.pop("messageId", UNSET)

        _created = d.pop("created", UNSET)
        created: datetime.datetime | Unset
        if isinstance(_created, Unset) or _created is None:
            created = UNSET
        else:
            created = isoparse(_created)

        _token_info = d.pop("tokenInfo", UNSET)
        token_info: TokenInfoDto | Unset
        if isinstance(_token_info, Unset) or _token_info is None:
            token_info = UNSET
        else:
            token_info = TokenInfoDto.from_dict(_token_info)

        _authorization_request_type = d.pop("authorizationRequestType", UNSET)
        authorization_request_type: ChargePointAuthorizeGetDtoAuthorizationRequestType | Unset
        if isinstance(_authorization_request_type, Unset) or _authorization_request_type is None:
            authorization_request_type = UNSET
        else:
            authorization_request_type = ChargePointAuthorizeGetDtoAuthorizationRequestType(_authorization_request_type)

        _authorization_result = d.pop("authorizationResult", UNSET)
        authorization_result: AuthorizationResultDto | Unset
        if isinstance(_authorization_result, Unset) or _authorization_result is None:
            authorization_result = UNSET
        else:
            authorization_result = AuthorizationResultDto.from_dict(_authorization_result)

        _context = d.pop("context", UNSET)
        context: AuthorizationContextDetailsDto | Unset
        if isinstance(_context, Unset) or _context is None:
            context = UNSET
        else:
            context = AuthorizationContextDetailsDto.from_dict(_context)

        charge_point_authorize_get_dto = cls(
            id=id,
            message_id=message_id,
            created=created,
            token_info=token_info,
            authorization_request_type=authorization_request_type,
            authorization_result=authorization_result,
            context=context,
        )

        charge_point_authorize_get_dto.additional_properties = d
        return charge_point_authorize_get_dto

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

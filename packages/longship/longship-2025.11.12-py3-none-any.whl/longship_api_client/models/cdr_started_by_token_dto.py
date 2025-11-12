from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.cdr_started_by_token_dto_auth_method import CdrStartedByTokenDtoAuthMethod
from ..models.cdr_started_by_token_dto_token_type import CdrStartedByTokenDtoTokenType
from ..types import UNSET, Unset

T = TypeVar("T", bound="CdrStartedByTokenDto")


@_attrs_define
class CdrStartedByTokenDto:
    """
    Attributes:
        uid (str | Unset):
        auth_reference (str | Unset):
        token_type (CdrStartedByTokenDtoTokenType | Unset):  Default: CdrStartedByTokenDtoTokenType.AD_HOC_USER.
        contract_id (str | Unset):
        auth_method (CdrStartedByTokenDtoAuthMethod | Unset):  Default: CdrStartedByTokenDtoAuthMethod.AUTH_REQUEST.
        provider_country_code (str | Unset):
        provider_party_id (str | Unset):
        token_ou_id (str | Unset):
        token_ou_name (str | Unset):
        token_ou (str | Unset):
    """

    uid: str | Unset = UNSET
    auth_reference: str | Unset = UNSET
    token_type: CdrStartedByTokenDtoTokenType | Unset = CdrStartedByTokenDtoTokenType.AD_HOC_USER
    contract_id: str | Unset = UNSET
    auth_method: CdrStartedByTokenDtoAuthMethod | Unset = CdrStartedByTokenDtoAuthMethod.AUTH_REQUEST
    provider_country_code: str | Unset = UNSET
    provider_party_id: str | Unset = UNSET
    token_ou_id: str | Unset = UNSET
    token_ou_name: str | Unset = UNSET
    token_ou: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uid = self.uid

        auth_reference = self.auth_reference

        token_type: str | Unset = UNSET
        if not isinstance(self.token_type, Unset):
            token_type = self.token_type.value

        contract_id = self.contract_id

        auth_method: str | Unset = UNSET
        if not isinstance(self.auth_method, Unset):
            auth_method = self.auth_method.value

        provider_country_code = self.provider_country_code

        provider_party_id = self.provider_party_id

        token_ou_id = self.token_ou_id

        token_ou_name = self.token_ou_name

        token_ou = self.token_ou

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if uid is not UNSET:
            field_dict["uid"] = uid
        if auth_reference is not UNSET:
            field_dict["authReference"] = auth_reference
        if token_type is not UNSET:
            field_dict["tokenType"] = token_type
        if contract_id is not UNSET:
            field_dict["contractId"] = contract_id
        if auth_method is not UNSET:
            field_dict["authMethod"] = auth_method
        if provider_country_code is not UNSET:
            field_dict["providerCountryCode"] = provider_country_code
        if provider_party_id is not UNSET:
            field_dict["providerPartyId"] = provider_party_id
        if token_ou_id is not UNSET:
            field_dict["tokenOUId"] = token_ou_id
        if token_ou_name is not UNSET:
            field_dict["tokenOUName"] = token_ou_name
        if token_ou is not UNSET:
            field_dict["tokenOU"] = token_ou

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        uid = d.pop("uid", UNSET)

        auth_reference = d.pop("authReference", UNSET)

        _token_type = d.pop("tokenType", UNSET)
        token_type: CdrStartedByTokenDtoTokenType | Unset
        if isinstance(_token_type, Unset) or _token_type is None:
            token_type = UNSET
        else:
            token_type = CdrStartedByTokenDtoTokenType(_token_type)

        contract_id = d.pop("contractId", UNSET)

        _auth_method = d.pop("authMethod", UNSET)
        auth_method: CdrStartedByTokenDtoAuthMethod | Unset
        if isinstance(_auth_method, Unset) or _auth_method is None:
            auth_method = UNSET
        else:
            auth_method = CdrStartedByTokenDtoAuthMethod(_auth_method)

        provider_country_code = d.pop("providerCountryCode", UNSET)

        provider_party_id = d.pop("providerPartyId", UNSET)

        token_ou_id = d.pop("tokenOUId", UNSET)

        token_ou_name = d.pop("tokenOUName", UNSET)

        token_ou = d.pop("tokenOU", UNSET)

        cdr_started_by_token_dto = cls(
            uid=uid,
            auth_reference=auth_reference,
            token_type=token_type,
            contract_id=contract_id,
            auth_method=auth_method,
            provider_country_code=provider_country_code,
            provider_party_id=provider_party_id,
            token_ou_id=token_ou_id,
            token_ou_name=token_ou_name,
            token_ou=token_ou,
        )

        cdr_started_by_token_dto.additional_properties = d
        return cdr_started_by_token_dto

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

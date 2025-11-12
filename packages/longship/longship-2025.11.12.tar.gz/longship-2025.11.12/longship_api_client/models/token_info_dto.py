from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.token_info_dto_token_type import TokenInfoDtoTokenType
from ..types import UNSET, Unset

T = TypeVar("T", bound="TokenInfoDto")


@_attrs_define
class TokenInfoDto:
    """
    Attributes:
        id_tag (str | Unset):
        contract_id (str | Unset):
        token_type (TokenInfoDtoTokenType | Unset):  Default: TokenInfoDtoTokenType.ADHOCUSER.
    """

    id_tag: str | Unset = UNSET
    contract_id: str | Unset = UNSET
    token_type: TokenInfoDtoTokenType | Unset = TokenInfoDtoTokenType.ADHOCUSER
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id_tag = self.id_tag

        contract_id = self.contract_id

        token_type: str | Unset = UNSET
        if not isinstance(self.token_type, Unset):
            token_type = self.token_type.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id_tag is not UNSET:
            field_dict["idTag"] = id_tag
        if contract_id is not UNSET:
            field_dict["contractId"] = contract_id
        if token_type is not UNSET:
            field_dict["tokenType"] = token_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id_tag = d.pop("idTag", UNSET)

        contract_id = d.pop("contractId", UNSET)

        _token_type = d.pop("tokenType", UNSET)
        token_type: TokenInfoDtoTokenType | Unset
        if isinstance(_token_type, Unset) or _token_type is None:
            token_type = UNSET
        else:
            token_type = TokenInfoDtoTokenType(_token_type)

        token_info_dto = cls(
            id_tag=id_tag,
            contract_id=contract_id,
            token_type=token_type,
        )

        token_info_dto.additional_properties = d
        return token_info_dto

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

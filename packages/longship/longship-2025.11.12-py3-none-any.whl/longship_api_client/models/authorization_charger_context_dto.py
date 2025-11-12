from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AuthorizationChargerContextDto")


@_attrs_define
class AuthorizationChargerContextDto:
    """
    Attributes:
        allow_any_token (bool | Unset):
        is_roaming (bool | Unset):
        charge_point_ou_code (str | Unset):
        reimburse_uid (str | Unset):
        reimburse_ou (str | Unset):
        has_reimbursement (bool | Unset):
    """

    allow_any_token: bool | Unset = UNSET
    is_roaming: bool | Unset = UNSET
    charge_point_ou_code: str | Unset = UNSET
    reimburse_uid: str | Unset = UNSET
    reimburse_ou: str | Unset = UNSET
    has_reimbursement: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        allow_any_token = self.allow_any_token

        is_roaming = self.is_roaming

        charge_point_ou_code = self.charge_point_ou_code

        reimburse_uid = self.reimburse_uid

        reimburse_ou = self.reimburse_ou

        has_reimbursement = self.has_reimbursement

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if allow_any_token is not UNSET:
            field_dict["allowAnyToken"] = allow_any_token
        if is_roaming is not UNSET:
            field_dict["isRoaming"] = is_roaming
        if charge_point_ou_code is not UNSET:
            field_dict["chargePointOUCode"] = charge_point_ou_code
        if reimburse_uid is not UNSET:
            field_dict["reimburseUid"] = reimburse_uid
        if reimburse_ou is not UNSET:
            field_dict["reimburseOu"] = reimburse_ou
        if has_reimbursement is not UNSET:
            field_dict["hasReimbursement"] = has_reimbursement

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        allow_any_token = d.pop("allowAnyToken", UNSET)

        is_roaming = d.pop("isRoaming", UNSET)

        charge_point_ou_code = d.pop("chargePointOUCode", UNSET)

        reimburse_uid = d.pop("reimburseUid", UNSET)

        reimburse_ou = d.pop("reimburseOu", UNSET)

        has_reimbursement = d.pop("hasReimbursement", UNSET)

        authorization_charger_context_dto = cls(
            allow_any_token=allow_any_token,
            is_roaming=is_roaming,
            charge_point_ou_code=charge_point_ou_code,
            reimburse_uid=reimburse_uid,
            reimburse_ou=reimburse_ou,
            has_reimbursement=has_reimbursement,
        )

        authorization_charger_context_dto.additional_properties = d
        return authorization_charger_context_dto

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

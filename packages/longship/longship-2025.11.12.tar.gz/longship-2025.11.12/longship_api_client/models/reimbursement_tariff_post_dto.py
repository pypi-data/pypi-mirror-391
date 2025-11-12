from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReimbursementTariffPostDto")


@_attrs_define
class ReimbursementTariffPostDto:
    """
    Attributes:
        currency (str):
        location_id (str):
        name (str | Unset):
        kwh_tariff (float | Unset):
        hubject_id (str | Unset):
        ocpi_id (str | Unset):
        external_reference (str | Unset):
    """

    currency: str
    location_id: str
    name: str | Unset = UNSET
    kwh_tariff: float | Unset = UNSET
    hubject_id: str | Unset = UNSET
    ocpi_id: str | Unset = UNSET
    external_reference: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        currency = self.currency

        location_id = self.location_id

        name = self.name

        kwh_tariff = self.kwh_tariff

        hubject_id = self.hubject_id

        ocpi_id = self.ocpi_id

        external_reference = self.external_reference

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "currency": currency,
                "locationId": location_id,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if kwh_tariff is not UNSET:
            field_dict["kwhTariff"] = kwh_tariff
        if hubject_id is not UNSET:
            field_dict["hubjectId"] = hubject_id
        if ocpi_id is not UNSET:
            field_dict["ocpiId"] = ocpi_id
        if external_reference is not UNSET:
            field_dict["externalReference"] = external_reference

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        currency = d.pop("currency")

        location_id = d.pop("locationId")

        name = d.pop("name", UNSET)

        kwh_tariff = d.pop("kwhTariff", UNSET)

        hubject_id = d.pop("hubjectId", UNSET)

        ocpi_id = d.pop("ocpiId", UNSET)

        external_reference = d.pop("externalReference", UNSET)

        reimbursement_tariff_post_dto = cls(
            currency=currency,
            location_id=location_id,
            name=name,
            kwh_tariff=kwh_tariff,
            hubject_id=hubject_id,
            ocpi_id=ocpi_id,
            external_reference=external_reference,
        )

        reimbursement_tariff_post_dto.additional_properties = d
        return reimbursement_tariff_post_dto

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

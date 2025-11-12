from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.tariff_distribution_history_dto import TariffDistributionHistoryDto


T = TypeVar("T", bound="TariffDistributionGetDto")


@_attrs_define
class TariffDistributionGetDto:
    """
    Attributes:
        id (str):
        name (str | Unset):
        ou_code (str | Unset):
        energy_compensation (float | Unset):
        fixed_tenant_k_wh_fee (float | Unset):
        percentage_fee_customer (float | Unset):
        percentage_fee_tenant (float | Unset):
        price_history (list[TariffDistributionHistoryDto] | Unset):
        created (datetime.datetime | Unset):
        deleted (datetime.datetime | Unset):
        updated (datetime.datetime | Unset):
    """

    id: str
    name: str | Unset = UNSET
    ou_code: str | Unset = UNSET
    energy_compensation: float | Unset = UNSET
    fixed_tenant_k_wh_fee: float | Unset = UNSET
    percentage_fee_customer: float | Unset = UNSET
    percentage_fee_tenant: float | Unset = UNSET
    price_history: list[TariffDistributionHistoryDto] | Unset = UNSET
    created: datetime.datetime | Unset = UNSET
    deleted: datetime.datetime | Unset = UNSET
    updated: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        ou_code = self.ou_code

        energy_compensation = self.energy_compensation

        fixed_tenant_k_wh_fee = self.fixed_tenant_k_wh_fee

        percentage_fee_customer = self.percentage_fee_customer

        percentage_fee_tenant = self.percentage_fee_tenant

        price_history: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.price_history, Unset):
            price_history = []
            for price_history_item_data in self.price_history:
                price_history_item = price_history_item_data.to_dict()
                price_history.append(price_history_item)

        created: str | Unset = UNSET
        if not isinstance(self.created, Unset):
            created = self.created.isoformat()

        deleted: str | Unset = UNSET
        if not isinstance(self.deleted, Unset):
            deleted = self.deleted.isoformat()

        updated: str | Unset = UNSET
        if not isinstance(self.updated, Unset):
            updated = self.updated.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if ou_code is not UNSET:
            field_dict["ouCode"] = ou_code
        if energy_compensation is not UNSET:
            field_dict["energyCompensation"] = energy_compensation
        if fixed_tenant_k_wh_fee is not UNSET:
            field_dict["fixedTenantKWhFee"] = fixed_tenant_k_wh_fee
        if percentage_fee_customer is not UNSET:
            field_dict["percentageFeeCustomer"] = percentage_fee_customer
        if percentage_fee_tenant is not UNSET:
            field_dict["percentageFeeTenant"] = percentage_fee_tenant
        if price_history is not UNSET:
            field_dict["priceHistory"] = price_history
        if created is not UNSET:
            field_dict["created"] = created
        if deleted is not UNSET:
            field_dict["deleted"] = deleted
        if updated is not UNSET:
            field_dict["updated"] = updated

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tariff_distribution_history_dto import TariffDistributionHistoryDto

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name", UNSET)

        ou_code = d.pop("ouCode", UNSET)

        energy_compensation = d.pop("energyCompensation", UNSET)

        fixed_tenant_k_wh_fee = d.pop("fixedTenantKWhFee", UNSET)

        percentage_fee_customer = d.pop("percentageFeeCustomer", UNSET)

        percentage_fee_tenant = d.pop("percentageFeeTenant", UNSET)

        price_history = []
        _price_history = d.pop("priceHistory", UNSET)
        for price_history_item_data in _price_history or []:
            price_history_item = TariffDistributionHistoryDto.from_dict(price_history_item_data)

            price_history.append(price_history_item)

        _created = d.pop("created", UNSET)
        created: datetime.datetime | Unset
        if isinstance(_created, Unset) or _created is None:
            created = UNSET
        else:
            created = isoparse(_created)

        _deleted = d.pop("deleted", UNSET)
        deleted: datetime.datetime | Unset
        if isinstance(_deleted, Unset) or _deleted is None:
            deleted = UNSET
        else:
            deleted = isoparse(_deleted)

        _updated = d.pop("updated", UNSET)
        updated: datetime.datetime | Unset
        if isinstance(_updated, Unset) or _updated is None:
            updated = UNSET
        else:
            updated = isoparse(_updated)

        tariff_distribution_get_dto = cls(
            id=id,
            name=name,
            ou_code=ou_code,
            energy_compensation=energy_compensation,
            fixed_tenant_k_wh_fee=fixed_tenant_k_wh_fee,
            percentage_fee_customer=percentage_fee_customer,
            percentage_fee_tenant=percentage_fee_tenant,
            price_history=price_history,
            created=created,
            deleted=deleted,
            updated=updated,
        )

        tariff_distribution_get_dto.additional_properties = d
        return tariff_distribution_get_dto

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

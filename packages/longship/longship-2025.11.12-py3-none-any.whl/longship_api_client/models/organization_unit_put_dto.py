from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.organization_unit_put_dto_ou_type import OrganizationUnitPutDtoOuType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.organization_unit_financial_details_dto import OrganizationUnitFinancialDetailsDto


T = TypeVar("T", bound="OrganizationUnitPutDto")


@_attrs_define
class OrganizationUnitPutDto:
    """
    Attributes:
        name (str | Unset): The name of the ou.
        ou_type (OrganizationUnitPutDtoOuType | Unset): This is the type of the OU: None(default), Company, Departement
            or Reimbursee.
        external_reference (str | Unset): This property can be used to link this OU to another system.
        grid_owner_reference (str | Unset): This property can be used to link this OU to a grid owner.
        tenant_reference (str | Unset): This property can be used to link this OU to a tenant.
        customer_reference (str | Unset): This property can be used to link this OU to a customer.
        address (str | Unset):
        state (str | Unset):
        country (str | Unset):
        city (str | Unset):
        house_number (str | Unset):
        postal_code (str | Unset):
        hotline_phone_number (str | Unset):
        company_email (str | Unset):
        primary_contactperson (str | Unset):
        primary_contactperson_email (str | Unset):
        msp_ou_id (str | Unset): The ou id used for the "Msp Integration" feature.
        msp_ou_name (str | Unset): The ou name used for the "Msp Integration" feature.
        msp_ou_code (str | Unset): The ou code used for the "Msp Integration" feature.
        msp_external_id (str | Unset): The externalId from the "Msp Integration" feature.
        financial_details (OrganizationUnitFinancialDetailsDto | Unset):
    """

    name: str | Unset = UNSET
    ou_type: OrganizationUnitPutDtoOuType | Unset = UNSET
    external_reference: str | Unset = UNSET
    grid_owner_reference: str | Unset = UNSET
    tenant_reference: str | Unset = UNSET
    customer_reference: str | Unset = UNSET
    address: str | Unset = UNSET
    state: str | Unset = UNSET
    country: str | Unset = UNSET
    city: str | Unset = UNSET
    house_number: str | Unset = UNSET
    postal_code: str | Unset = UNSET
    hotline_phone_number: str | Unset = UNSET
    company_email: str | Unset = UNSET
    primary_contactperson: str | Unset = UNSET
    primary_contactperson_email: str | Unset = UNSET
    msp_ou_id: str | Unset = UNSET
    msp_ou_name: str | Unset = UNSET
    msp_ou_code: str | Unset = UNSET
    msp_external_id: str | Unset = UNSET
    financial_details: OrganizationUnitFinancialDetailsDto | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        ou_type: str | Unset = UNSET
        if not isinstance(self.ou_type, Unset):
            ou_type = self.ou_type.value

        external_reference = self.external_reference

        grid_owner_reference = self.grid_owner_reference

        tenant_reference = self.tenant_reference

        customer_reference = self.customer_reference

        address = self.address

        state = self.state

        country = self.country

        city = self.city

        house_number = self.house_number

        postal_code = self.postal_code

        hotline_phone_number = self.hotline_phone_number

        company_email = self.company_email

        primary_contactperson = self.primary_contactperson

        primary_contactperson_email = self.primary_contactperson_email

        msp_ou_id = self.msp_ou_id

        msp_ou_name = self.msp_ou_name

        msp_ou_code = self.msp_ou_code

        msp_external_id = self.msp_external_id

        financial_details: dict[str, Any] | Unset = UNSET
        if not isinstance(self.financial_details, Unset):
            financial_details = self.financial_details.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if ou_type is not UNSET:
            field_dict["ouType"] = ou_type
        if external_reference is not UNSET:
            field_dict["externalReference"] = external_reference
        if grid_owner_reference is not UNSET:
            field_dict["gridOwnerReference"] = grid_owner_reference
        if tenant_reference is not UNSET:
            field_dict["tenantReference"] = tenant_reference
        if customer_reference is not UNSET:
            field_dict["customerReference"] = customer_reference
        if address is not UNSET:
            field_dict["address"] = address
        if state is not UNSET:
            field_dict["state"] = state
        if country is not UNSET:
            field_dict["country"] = country
        if city is not UNSET:
            field_dict["city"] = city
        if house_number is not UNSET:
            field_dict["houseNumber"] = house_number
        if postal_code is not UNSET:
            field_dict["postalCode"] = postal_code
        if hotline_phone_number is not UNSET:
            field_dict["hotlinePhoneNumber"] = hotline_phone_number
        if company_email is not UNSET:
            field_dict["companyEmail"] = company_email
        if primary_contactperson is not UNSET:
            field_dict["primaryContactperson"] = primary_contactperson
        if primary_contactperson_email is not UNSET:
            field_dict["primaryContactpersonEmail"] = primary_contactperson_email
        if msp_ou_id is not UNSET:
            field_dict["mspOuId"] = msp_ou_id
        if msp_ou_name is not UNSET:
            field_dict["mspOuName"] = msp_ou_name
        if msp_ou_code is not UNSET:
            field_dict["mspOuCode"] = msp_ou_code
        if msp_external_id is not UNSET:
            field_dict["mspExternalId"] = msp_external_id
        if financial_details is not UNSET:
            field_dict["financialDetails"] = financial_details

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.organization_unit_financial_details_dto import OrganizationUnitFinancialDetailsDto

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        _ou_type = d.pop("ouType", UNSET)
        ou_type: OrganizationUnitPutDtoOuType | Unset
        if isinstance(_ou_type, Unset) or _ou_type is None:
            ou_type = UNSET
        else:
            ou_type = OrganizationUnitPutDtoOuType(_ou_type)

        external_reference = d.pop("externalReference", UNSET)

        grid_owner_reference = d.pop("gridOwnerReference", UNSET)

        tenant_reference = d.pop("tenantReference", UNSET)

        customer_reference = d.pop("customerReference", UNSET)

        address = d.pop("address", UNSET)

        state = d.pop("state", UNSET)

        country = d.pop("country", UNSET)

        city = d.pop("city", UNSET)

        house_number = d.pop("houseNumber", UNSET)

        postal_code = d.pop("postalCode", UNSET)

        hotline_phone_number = d.pop("hotlinePhoneNumber", UNSET)

        company_email = d.pop("companyEmail", UNSET)

        primary_contactperson = d.pop("primaryContactperson", UNSET)

        primary_contactperson_email = d.pop("primaryContactpersonEmail", UNSET)

        msp_ou_id = d.pop("mspOuId", UNSET)

        msp_ou_name = d.pop("mspOuName", UNSET)

        msp_ou_code = d.pop("mspOuCode", UNSET)

        msp_external_id = d.pop("mspExternalId", UNSET)

        _financial_details = d.pop("financialDetails", UNSET)
        financial_details: OrganizationUnitFinancialDetailsDto | Unset
        if isinstance(_financial_details, Unset) or _financial_details is None:
            financial_details = UNSET
        else:
            financial_details = OrganizationUnitFinancialDetailsDto.from_dict(_financial_details)

        organization_unit_put_dto = cls(
            name=name,
            ou_type=ou_type,
            external_reference=external_reference,
            grid_owner_reference=grid_owner_reference,
            tenant_reference=tenant_reference,
            customer_reference=customer_reference,
            address=address,
            state=state,
            country=country,
            city=city,
            house_number=house_number,
            postal_code=postal_code,
            hotline_phone_number=hotline_phone_number,
            company_email=company_email,
            primary_contactperson=primary_contactperson,
            primary_contactperson_email=primary_contactperson_email,
            msp_ou_id=msp_ou_id,
            msp_ou_name=msp_ou_name,
            msp_ou_code=msp_ou_code,
            msp_external_id=msp_external_id,
            financial_details=financial_details,
        )

        organization_unit_put_dto.additional_properties = d
        return organization_unit_put_dto

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

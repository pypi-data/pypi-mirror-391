from enum import Enum


class OrganizationUnitPutDtoOuType(str, Enum):
    COMPANY = "Company"
    DEPARTEMENT = "Departement"
    NONE = "None"
    REIMBURSEE = "Reimbursee"

    def __str__(self) -> str:
        return str(self.value)

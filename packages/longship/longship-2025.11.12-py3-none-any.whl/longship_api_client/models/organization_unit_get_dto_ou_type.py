from enum import Enum


class OrganizationUnitGetDtoOuType(str, Enum):
    COMPANY = "Company"
    DEPARTEMENT = "Departement"
    NONE = "None"
    REIMBURSEE = "Reimbursee"

    def __str__(self) -> str:
        return str(self.value)

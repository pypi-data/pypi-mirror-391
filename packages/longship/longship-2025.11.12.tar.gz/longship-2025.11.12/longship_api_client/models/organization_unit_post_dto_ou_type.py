from enum import Enum


class OrganizationUnitPostDtoOuType(str, Enum):
    COMPANY = "Company"
    DEPARTEMENT = "Departement"
    NONE = "None"
    REIMBURSEE = "Reimbursee"

    def __str__(self) -> str:
        return str(self.value)

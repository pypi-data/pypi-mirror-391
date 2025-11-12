from enum import Enum


class TariffDtoReimburseType(str, Enum):
    NONE = "NONE"
    ORGANIZATIONUNIT = "ORGANIZATIONUNIT"
    TOKEN = "TOKEN"

    def __str__(self) -> str:
        return str(self.value)

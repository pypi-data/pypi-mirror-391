from enum import Enum


class TariffPutDtoReimburseType(str, Enum):
    NONE = "NONE"
    ORGANIZATIONUNIT = "ORGANIZATIONUNIT"
    TOKEN = "TOKEN"

    def __str__(self) -> str:
        return str(self.value)

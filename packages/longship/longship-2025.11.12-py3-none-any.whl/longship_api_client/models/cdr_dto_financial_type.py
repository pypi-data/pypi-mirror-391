from enum import Enum


class CdrDtoFinancialType(str, Enum):
    CREDIT = "Credit"
    DEBIT = "Debit"

    def __str__(self) -> str:
        return str(self.value)

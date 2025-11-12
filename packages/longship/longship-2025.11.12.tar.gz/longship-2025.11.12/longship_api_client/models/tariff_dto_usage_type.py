from enum import Enum


class TariffDtoUsageType(str, Enum):
    BUY = "BUY"
    DEFAULT = "DEFAULT"
    REIMBURSE = "REIMBURSE"
    SELL = "SELL"
    SELLCUSTOM = "SELLCUSTOM"
    SELLPRIVATE = "SELLPRIVATE"

    def __str__(self) -> str:
        return str(self.value)

from enum import Enum


class TariffPostDtoTariffType(str, Enum):
    AD_HOC_PAYMENT = "AD_HOC_PAYMENT"
    REGULAR = "REGULAR"

    def __str__(self) -> str:
        return str(self.value)

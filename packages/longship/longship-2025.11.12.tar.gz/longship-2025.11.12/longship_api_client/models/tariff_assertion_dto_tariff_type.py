from enum import Enum


class TariffAssertionDtoTariffType(str, Enum):
    DEFAULTTARIFF = "DefaultTariff"
    DYNAMICTARIFF = "DynamicTariff"
    PRIVATETARIFF = "PrivateTariff"
    REIMBURSEMENTTARIFF = "ReimbursementTariff"
    SELLCUSTOMTARIFF = "SellCustomTariff"
    SELLTARIFF = "SellTariff"

    def __str__(self) -> str:
        return str(self.value)

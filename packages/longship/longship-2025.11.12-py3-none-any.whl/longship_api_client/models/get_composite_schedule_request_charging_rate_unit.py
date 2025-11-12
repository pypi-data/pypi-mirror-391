from enum import Enum


class GetCompositeScheduleRequestChargingRateUnit(str, Enum):
    A = "A"
    W = "W"

    def __str__(self) -> str:
        return str(self.value)

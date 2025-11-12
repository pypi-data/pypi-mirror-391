from enum import Enum


class ChargingScheduleChargingRateUnit(str, Enum):
    A = "A"
    W = "W"

    def __str__(self) -> str:
        return str(self.value)

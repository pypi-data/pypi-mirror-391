from enum import Enum


class ChargingProfileChargingProfileKind(str, Enum):
    ABSOLUTE = "Absolute"
    RECURRING = "Recurring"
    RELATIVE = "Relative"

    def __str__(self) -> str:
        return str(self.value)

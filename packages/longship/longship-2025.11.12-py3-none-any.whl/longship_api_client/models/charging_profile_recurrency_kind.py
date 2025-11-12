from enum import Enum


class ChargingProfileRecurrencyKind(str, Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"

    def __str__(self) -> str:
        return str(self.value)

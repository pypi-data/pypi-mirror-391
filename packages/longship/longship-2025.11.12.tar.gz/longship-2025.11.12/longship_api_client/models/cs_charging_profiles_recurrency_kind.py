from enum import Enum


class CsChargingProfilesRecurrencyKind(str, Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"

    def __str__(self) -> str:
        return str(self.value)

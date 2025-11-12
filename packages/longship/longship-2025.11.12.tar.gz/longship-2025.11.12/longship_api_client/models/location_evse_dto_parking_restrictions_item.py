from enum import Enum


class LocationEVSEDtoParkingRestrictionsItem(str, Enum):
    CUSTOMERS = "CUSTOMERS"
    DISABLED = "DISABLED"
    EV_ONLY = "EV_ONLY"
    MOTORCYCLES = "MOTORCYCLES"
    PLUGGED = "PLUGGED"

    def __str__(self) -> str:
        return str(self.value)

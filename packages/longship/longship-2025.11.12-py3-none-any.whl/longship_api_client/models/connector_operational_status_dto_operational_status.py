from enum import Enum


class ConnectorOperationalStatusDtoOperationalStatus(str, Enum):
    AVAILABLE = "Available"
    CHARGING = "Charging"
    FAULTED = "Faulted"
    FINISHING = "Finishing"
    PREPARING = "Preparing"
    RESERVED = "Reserved"
    SUSPENDEDEV = "SuspendedEV"
    SUSPENDEDEVSE = "SuspendedEVSE"
    UNAVAILABLE = "Unavailable"

    def __str__(self) -> str:
        return str(self.value)

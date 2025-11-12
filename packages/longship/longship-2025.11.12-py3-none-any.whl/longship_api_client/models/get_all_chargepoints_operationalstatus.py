from enum import Enum


class GetAllChargepointsOperationalstatus(str, Enum):
    AVAILABLE = "available"
    CHARGING = "charging"
    FAULTED = "faulted"
    FINISHING = "finishing"
    PREPARING = "preparing"
    RESERVED = "reserved"
    SUSPENDEDEV = "suspendedEV"
    SUSPENDEDEVSE = "suspendedEVSE"
    UNAVAILABLE = "unavailable"

    def __str__(self) -> str:
        return str(self.value)

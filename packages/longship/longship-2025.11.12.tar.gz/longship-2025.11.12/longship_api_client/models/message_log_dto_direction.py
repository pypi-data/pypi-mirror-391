from enum import Enum


class MessageLogDtoDirection(str, Enum):
    CHARGERTOCPO = "ChargerToCpo"
    CPOTOCHARGER = "CpoToCharger"
    UNKNOWN = "Unknown"

    def __str__(self) -> str:
        return str(self.value)

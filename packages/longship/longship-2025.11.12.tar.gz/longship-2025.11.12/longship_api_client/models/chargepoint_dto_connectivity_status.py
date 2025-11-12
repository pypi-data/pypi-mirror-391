from enum import Enum


class ChargepointDtoConnectivityStatus(str, Enum):
    OFFLINE = "OFFLINE"
    ONLINE = "ONLINE"

    def __str__(self) -> str:
        return str(self.value)

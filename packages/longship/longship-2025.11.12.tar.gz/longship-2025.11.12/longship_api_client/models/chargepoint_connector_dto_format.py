from enum import Enum


class ChargepointConnectorDtoFormat(str, Enum):
    CABLE = "CABLE"
    SOCKET = "SOCKET"

    def __str__(self) -> str:
        return str(self.value)

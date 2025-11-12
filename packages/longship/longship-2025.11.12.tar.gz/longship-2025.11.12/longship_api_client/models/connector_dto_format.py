from enum import Enum


class ConnectorDtoFormat(str, Enum):
    CABLE = "CABLE"
    SOCKET = "SOCKET"

    def __str__(self) -> str:
        return str(self.value)

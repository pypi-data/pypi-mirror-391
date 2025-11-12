from enum import Enum


class StartedByInfoDtoRoamingPlatformType(str, Enum):
    HUBJECT = "Hubject"
    OCPI = "Ocpi"

    def __str__(self) -> str:
        return str(self.value)

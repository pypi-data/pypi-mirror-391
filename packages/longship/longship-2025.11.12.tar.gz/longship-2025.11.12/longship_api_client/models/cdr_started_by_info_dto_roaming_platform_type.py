from enum import Enum


class CdrStartedByInfoDtoRoamingPlatformType(str, Enum):
    HUBJECT = "Hubject"
    OCPI = "Ocpi"

    def __str__(self) -> str:
        return str(self.value)

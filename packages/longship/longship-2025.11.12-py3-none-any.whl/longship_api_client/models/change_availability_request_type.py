from enum import Enum


class ChangeAvailabilityRequestType(str, Enum):
    INOPERATIVE = "Inoperative"
    OPERATIVE = "Operative"

    def __str__(self) -> str:
        return str(self.value)

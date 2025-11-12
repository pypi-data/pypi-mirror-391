from enum import Enum


class SendLocalListRequestUpdateType(str, Enum):
    DIFFERENTIAL = "Differential"
    FULL = "Full"

    def __str__(self) -> str:
        return str(self.value)

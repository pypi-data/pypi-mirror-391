from enum import Enum


class ResetRequestType(str, Enum):
    HARD = "Hard"
    SOFT = "Soft"

    def __str__(self) -> str:
        return str(self.value)

from enum import Enum


class GetAllSessionsV2OrderBy(str, Enum):
    START = "start"
    STOP = "stop"

    def __str__(self) -> str:
        return str(self.value)

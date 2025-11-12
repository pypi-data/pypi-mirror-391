from enum import Enum


class GetAllSessionsOrderBy(str, Enum):
    START = "start"
    STOP = "stop"

    def __str__(self) -> str:
        return str(self.value)

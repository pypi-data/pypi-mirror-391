from enum import Enum


class SessionStatusUpdateRequestDtoStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    INVALID = "INVALID"
    PENDING = "PENDING"
    RESERVATION = "RESERVATION"

    def __str__(self) -> str:
        return str(self.value)

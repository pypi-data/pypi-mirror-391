from enum import Enum


class AuthorizationResultDtoStatus(str, Enum):
    ACCEPTED = "Accepted"
    BLOCKED = "Blocked"
    CONCURRENTTX = "ConcurrentTx"
    EXPIRED = "Expired"
    INVALID = "Invalid"
    PENDING = "Pending"

    def __str__(self) -> str:
        return str(self.value)

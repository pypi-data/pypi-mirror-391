from enum import Enum


class IdTagInfoStatus(str, Enum):
    ACCEPTED = "Accepted"
    BLOCKED = "Blocked"
    CONCURRENTTX = "ConcurrentTx"
    EXPIRED = "Expired"
    INVALID = "Invalid"

    def __str__(self) -> str:
        return str(self.value)

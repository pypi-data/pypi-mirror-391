from enum import Enum


class AuthorizationAssertionDtoStatus(str, Enum):
    INVALID = "Invalid"
    PENDING = "Pending"
    SKIPPED = "Skipped"
    TIMEOUT = "Timeout"
    VALID = "Valid"
    VERIFIED = "Verified"

    def __str__(self) -> str:
        return str(self.value)

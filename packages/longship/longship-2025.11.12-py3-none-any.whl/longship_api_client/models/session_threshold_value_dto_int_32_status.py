from enum import Enum


class SessionThresholdValueDtoInt32Status(str, Enum):
    APPROVED = "Approved"
    PENDING = "Pending"
    REJECTED = "Rejected"
    SKIPPED = "Skipped"
    SUSPICIOUS = "Suspicious"

    def __str__(self) -> str:
        return str(self.value)

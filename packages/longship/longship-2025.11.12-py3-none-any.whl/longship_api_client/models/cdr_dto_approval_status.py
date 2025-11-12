from enum import Enum


class CdrDtoApprovalStatus(str, Enum):
    APPROVED = "Approved"
    REJECTED = "Rejected"

    def __str__(self) -> str:
        return str(self.value)

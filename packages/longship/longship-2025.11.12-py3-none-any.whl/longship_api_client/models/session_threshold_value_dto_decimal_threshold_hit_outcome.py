from enum import Enum


class SessionThresholdValueDtoDecimalThresholdHitOutcome(str, Enum):
    REJECTED = "Rejected"
    SUSPICIOUS = "Suspicious"

    def __str__(self) -> str:
        return str(self.value)

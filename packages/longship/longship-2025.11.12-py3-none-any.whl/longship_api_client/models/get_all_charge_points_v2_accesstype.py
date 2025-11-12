from enum import Enum


class GetAllChargePointsV2Accesstype(str, Enum):
    GUEST = "guest"
    PRIVATE = "private"
    PUBLIC = "public"

    def __str__(self) -> str:
        return str(self.value)

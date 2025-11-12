from enum import Enum


class GetAllChargePointsV2SearchProperty(str, Enum):
    CHARGEPOINTID = "chargePointId"
    DISPLAYNAME = "displayName"
    OU = "ou"
    ROAMINGNAME = "roamingName"

    def __str__(self) -> str:
        return str(self.value)

from enum import Enum


class GetAllSessionsV2SearchProperty(str, Enum):
    CHARGEPOINTID = "chargePointId"
    CONTRACTID = "contractId"
    SESSIONID = "sessionId"
    TOKEN = "token"

    def __str__(self) -> str:
        return str(self.value)

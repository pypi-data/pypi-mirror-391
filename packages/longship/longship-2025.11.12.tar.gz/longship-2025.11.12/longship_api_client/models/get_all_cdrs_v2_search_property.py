from enum import Enum


class GetAllCdrsV2SearchProperty(str, Enum):
    CDRID = "cdrId"
    CHARGEPOINTID = "chargePointId"
    CONTRACTID = "contractId"
    TOKEN = "token"

    def __str__(self) -> str:
        return str(self.value)

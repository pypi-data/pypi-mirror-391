from enum import Enum


class ClearChargingProfileRequestChargingProfilePurpose(str, Enum):
    CHARGEPOINTMAXPROFILE = "ChargePointMaxProfile"
    TXDEFAULTPROFILE = "TxDefaultProfile"
    TXPROFILE = "TxProfile"

    def __str__(self) -> str:
        return str(self.value)

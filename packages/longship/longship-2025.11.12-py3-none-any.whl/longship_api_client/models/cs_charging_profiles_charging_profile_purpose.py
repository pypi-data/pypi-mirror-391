from enum import Enum


class CsChargingProfilesChargingProfilePurpose(str, Enum):
    CHARGEPOINTMAXPROFILE = "ChargePointMaxProfile"
    TXDEFAULTPROFILE = "TxDefaultProfile"
    TXPROFILE = "TxProfile"

    def __str__(self) -> str:
        return str(self.value)

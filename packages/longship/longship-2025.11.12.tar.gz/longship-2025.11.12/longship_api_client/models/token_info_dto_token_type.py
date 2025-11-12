from enum import Enum


class TokenInfoDtoTokenType(str, Enum):
    ADHOCUSER = "AdHocUser"
    APPUSER = "AppUser"
    OTHER = "Other"
    RFID = "Rfid"

    def __str__(self) -> str:
        return str(self.value)

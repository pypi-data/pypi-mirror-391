from enum import Enum


class PublishTokenTypeDtoType(str, Enum):
    AD_HOC_USER = "AD_HOC_USER"
    APP_USER = "APP_USER"
    OTHER = "OTHER"
    RFID = "RFID"

    def __str__(self) -> str:
        return str(self.value)

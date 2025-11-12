from enum import Enum


class ImageDtoCategory(str, Enum):
    CHARGER = "CHARGER"
    ENTRANCE = "ENTRANCE"
    LOCATION = "LOCATION"
    NETWORK = "NETWORK"
    OPERATOR = "OPERATOR"
    OTHER = "OTHER"
    OWNER = "OWNER"

    def __str__(self) -> str:
        return str(self.value)

from enum import Enum


class LocationPutDtoParkingType(str, Enum):
    ALONG_MOTORWAY = "ALONG_MOTORWAY"
    ON_DRIVEWAY = "ON_DRIVEWAY"
    ON_STREET = "ON_STREET"
    PARKING_GARAGE = "PARKING_GARAGE"
    PARKING_LOT = "PARKING_LOT"
    UNDERGROUND_GARAGE = "UNDERGROUND_GARAGE"

    def __str__(self) -> str:
        return str(self.value)

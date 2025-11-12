from enum import Enum


class GetAllLocationsV2SearchProperty(str, Enum):
    CITY = "city"
    COUNTRYCODE = "countryCode"
    LOCATIONID = "locationId"
    NAME = "name"
    POSTALCODE = "postalCode"
    STATE = "state"
    STREET = "street"

    def __str__(self) -> str:
        return str(self.value)

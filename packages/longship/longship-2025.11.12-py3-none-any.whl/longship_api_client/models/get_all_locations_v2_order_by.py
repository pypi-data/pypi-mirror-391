from enum import Enum


class GetAllLocationsV2OrderBy(str, Enum):
    ADDRESS = "address"
    LASTUPDATED = "lastupdated"
    NAME = "name"
    OUNAME = "ouname"

    def __str__(self) -> str:
        return str(self.value)

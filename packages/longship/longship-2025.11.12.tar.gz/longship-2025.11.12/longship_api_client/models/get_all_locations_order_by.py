from enum import Enum


class GetAllLocationsOrderBy(str, Enum):
    ADDRESS = "address"
    LASTUPDATED = "lastupdated"
    NAME = "name"
    OUNAME = "ouname"

    def __str__(self) -> str:
        return str(self.value)

from enum import Enum


class GetAllTariffdistributionsOrderBy(str, Enum):
    ENERGY_COMPENSATION = "energY_COMPENSATION"
    NAME = "name"
    TYPE = "type"

    def __str__(self) -> str:
        return str(self.value)

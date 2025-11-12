from enum import Enum


class GetAllTariffsOrderBy(str, Enum):
    CREATED = "created"
    KWH_PRICE = "kwH_PRICE"
    MODIFIED = "modified"
    NAME = "name"
    START_PRICE = "starT_PRICE"

    def __str__(self) -> str:
        return str(self.value)

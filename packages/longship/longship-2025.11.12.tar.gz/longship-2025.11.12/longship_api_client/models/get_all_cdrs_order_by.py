from enum import Enum


class GetAllCdrsOrderBy(str, Enum):
    ENDDATETIME = "enddatetime"
    STARTDATETIME = "startdatetime"

    def __str__(self) -> str:
        return str(self.value)

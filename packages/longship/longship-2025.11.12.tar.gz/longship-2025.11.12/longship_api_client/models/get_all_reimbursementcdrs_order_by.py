from enum import Enum


class GetAllReimbursementcdrsOrderBy(str, Enum):
    ENDDATETIME = "enddatetime"
    STARTDATETIME = "startdatetime"

    def __str__(self) -> str:
        return str(self.value)

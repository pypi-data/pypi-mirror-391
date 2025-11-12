from enum import Enum


class GetAllCdrsV2OrderBy(str, Enum):
    ENDDATETIME = "enddatetime"
    STARTDATETIME = "startdatetime"

    def __str__(self) -> str:
        return str(self.value)

from enum import Enum


class GetAllReimbursementCdrsV2OrderBy(str, Enum):
    ENDDATETIME = "enddatetime"
    STARTDATETIME = "startdatetime"

    def __str__(self) -> str:
        return str(self.value)

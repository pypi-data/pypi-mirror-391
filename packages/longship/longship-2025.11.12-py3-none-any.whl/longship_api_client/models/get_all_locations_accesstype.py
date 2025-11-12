from enum import Enum


class GetAllLocationsAccesstype(str, Enum):
    GUEST = "guest"
    PRIVATE = "private"
    PUBLIC = "public"
    REIMBURSEMENT = "reimbursement"

    def __str__(self) -> str:
        return str(self.value)

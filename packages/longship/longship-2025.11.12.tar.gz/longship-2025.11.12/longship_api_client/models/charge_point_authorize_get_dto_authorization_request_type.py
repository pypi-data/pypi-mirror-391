from enum import Enum


class ChargePointAuthorizeGetDtoAuthorizationRequestType(str, Enum):
    AUTHORIZE = "Authorize"
    MANUAL = "Manual"
    STARTTRANSACTION = "StartTransaction"

    def __str__(self) -> str:
        return str(self.value)

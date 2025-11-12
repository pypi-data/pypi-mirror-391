from enum import Enum


class CdrStartedByTokenDtoAuthMethod(str, Enum):
    AUTH_REQUEST = "AUTH_REQUEST"
    COMMAND = "COMMAND"
    WHITELIST = "WHITELIST"

    def __str__(self) -> str:
        return str(self.value)

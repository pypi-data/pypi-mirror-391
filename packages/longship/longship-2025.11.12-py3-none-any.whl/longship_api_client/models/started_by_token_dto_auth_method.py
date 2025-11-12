from enum import Enum


class StartedByTokenDtoAuthMethod(str, Enum):
    AUTH_REQUEST = "AUTH_REQUEST"
    COMMAND = "COMMAND"
    WHITELIST = "WHITELIST"

    def __str__(self) -> str:
        return str(self.value)

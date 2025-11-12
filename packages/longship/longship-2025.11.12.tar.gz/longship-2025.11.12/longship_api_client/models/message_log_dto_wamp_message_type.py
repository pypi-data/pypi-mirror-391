from enum import Enum


class MessageLogDtoWampMessageType(str, Enum):
    ERROR = "Error"
    REQUEST = "Request"
    RESPONSE = "Response"
    UNKNOWN = "Unknown"

    def __str__(self) -> str:
        return str(self.value)

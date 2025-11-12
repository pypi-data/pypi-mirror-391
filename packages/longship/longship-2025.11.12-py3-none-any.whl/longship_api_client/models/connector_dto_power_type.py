from enum import Enum


class ConnectorDtoPowerType(str, Enum):
    AC_1_PHASE = "AC_1_PHASE"
    AC_3_PHASE = "AC_3_PHASE"
    DC = "DC"

    def __str__(self) -> str:
        return str(self.value)

from enum import Enum


class EnergySourceDtoSource(str, Enum):
    COAL = "COAL"
    GAS = "GAS"
    GENERAL_FOSSIL = "GENERAL_FOSSIL"
    GENERAL_GREEN = "GENERAL_GREEN"
    NUCLEAR = "NUCLEAR"
    SOLAR = "SOLAR"
    WATER = "WATER"
    WIND = "WIND"

    def __str__(self) -> str:
        return str(self.value)

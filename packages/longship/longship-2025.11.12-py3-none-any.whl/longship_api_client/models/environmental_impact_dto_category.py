from enum import Enum


class EnvironmentalImpactDtoCategory(str, Enum):
    CARBON_DIOXIDE = "CARBON_DIOXIDE"
    NUCLEAR_WASTE = "NUCLEAR_WASTE"

    def __str__(self) -> str:
        return str(self.value)

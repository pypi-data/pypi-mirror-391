from enum import Enum


class PriceComponentPricingType(str, Enum):
    ENERGY = "ENERGY"
    FLAT = "FLAT"
    PARKING_TIME = "PARKING_TIME"
    TIME = "TIME"

    def __str__(self) -> str:
        return str(self.value)

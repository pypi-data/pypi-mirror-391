from enum import Enum


class ChargingMeterValueDtoUnit(str, Enum):
    A = "A"
    CELCIUS = "Celcius"
    FAHRENHEIT = "Fahrenheit"
    K = "K"
    KVA = "kVA"
    KVAR = "kvar"
    KVARH = "kvarh"
    KW = "kW"
    KWH = "kWh"
    PERCENT = "Percent"
    V = "V"
    VA = "VA"
    VAR = "var"
    VARH = "varh"
    W = "W"
    WH = "Wh"

    def __str__(self) -> str:
        return str(self.value)

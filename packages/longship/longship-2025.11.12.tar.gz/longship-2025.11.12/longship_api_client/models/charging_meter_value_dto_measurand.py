from enum import Enum


class ChargingMeterValueDtoMeasurand(str, Enum):
    CURRENT_EXPORT = "Current.Export"
    CURRENT_IMPORT = "Current.Import"
    CURRENT_OFFERED = "Current.Offered"
    ENERGY_ACTIVE_EXPORT_INTERVAL = "Energy.Active.Export.Interval"
    ENERGY_ACTIVE_EXPORT_REGISTER = "Energy.Active.Export.Register"
    ENERGY_ACTIVE_IMPORT_INTERVAL = "Energy.Active.Import.Interval"
    ENERGY_ACTIVE_IMPORT_REGISTER = "Energy.Active.Import.Register"
    ENERGY_REACTIVE_EXPORT_INTERVAL = "Energy.Reactive.Export.Interval"
    ENERGY_REACTIVE_EXPORT_REGISTER = "Energy.Reactive.Export.Register"
    ENERGY_REACTIVE_IMPORT_INTERVAL = "Energy.Reactive.Import.Interval"
    ENERGY_REACTIVE_IMPORT_REGISTER = "Energy.Reactive.Import.Register"
    FREQUENCY = "Frequency"
    POWER_ACTIVE_EXPORT = "Power.Active.Export"
    POWER_ACTIVE_IMPORT = "Power.Active.Import"
    POWER_FACTOR = "Power.Factor"
    POWER_OFFERED = "Power.Offered"
    POWER_REACTIVE_EXPORT = "Power.Reactive.Export"
    POWER_REACTIVE_IMPORT = "Power.Reactive.Import"
    RPM = "RPM"
    SOC = "SoC"
    TEMPERATURE = "Temperature"
    VOLTAGE = "Voltage"

    def __str__(self) -> str:
        return str(self.value)

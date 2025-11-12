from enum import Enum


class TriggerMessageRequestRequestedMessage(str, Enum):
    BOOTNOTIFICATION = "BootNotification"
    DIAGNOSTICSSTATUSNOTIFICATION = "DiagnosticsStatusNotification"
    FIRMWARESTATUSNOTIFICATION = "FirmwareStatusNotification"
    HEARTBEAT = "Heartbeat"
    METERVALUES = "MeterValues"
    STATUSNOTIFICATION = "StatusNotification"

    def __str__(self) -> str:
        return str(self.value)

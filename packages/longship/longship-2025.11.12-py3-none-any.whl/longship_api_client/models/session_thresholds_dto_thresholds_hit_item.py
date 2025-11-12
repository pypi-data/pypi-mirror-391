from enum import Enum


class SessionThresholdsDtoThresholdsHitItem(str, Enum):
    CHECKCHARGINGSPEED = "CheckChargingSpeed"
    CHECKSESSIONINFUTURE = "CheckSessionInFuture"
    MAXKWHAC = "MaxKwhAc"
    MAXKWHDC = "MaxKwhDc"
    MAXSESSIONAGEINDAYS = "MaxSessionAgeInDays"
    MINDURATIONAC = "MinDurationAc"
    MINDURATIONDC = "MinDurationDc"
    MINKWHAC = "MinKwhAc"
    MINKWHDC = "MinKwhDc"

    def __str__(self) -> str:
        return str(self.value)

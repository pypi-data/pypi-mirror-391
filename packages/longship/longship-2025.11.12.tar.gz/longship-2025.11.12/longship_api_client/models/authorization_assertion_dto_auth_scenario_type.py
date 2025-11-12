from enum import Enum


class AuthorizationAssertionDtoAuthScenarioType(str, Enum):
    CHARGERALLOWANY = "ChargerAllowAny"
    EXISTINGHUBJECTAPPROVAL = "ExistingHubjectApproval"
    HUBJECTFASTAPPROVAL = "HubjectFastApproval"
    LOCALTOKEN = "LocalToken"
    MSPBLOCKED = "MspBlocked"
    NEWTOKENVALIDATIONREQUEST = "NewTokenValidationRequest"
    NOAPPROVALS = "NoApprovals"
    NONE = "None"
    RECENTPLUGANDCHARGEAPPROVAL = "RecentPlugAndChargeApproval"
    REIMBURSEMENT = "Reimbursement"
    REMOTESTARTTOKEN = "RemoteStartToken"
    WHITELISTEDTOKEN = "WhitelistedToken"

    def __str__(self) -> str:
        return str(self.value)

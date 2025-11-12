from enum import Enum


class StartedByInfoDtoAuthorizationState(str, Enum):
    APPROVEDBYALLOWANY = "ApprovedByAllowAny"
    APPROVEDBYAUTHREQUEST = "ApprovedByAuthRequest"
    APPROVEDBYLOCALTOKEN = "ApprovedByLocalToken"
    APPROVEDBYREMOTE = "ApprovedByRemote"
    APPROVEDBYROAMINGPARTNER = "ApprovedByRoamingPartner"
    ERRORINVALIDLOCALTOKEN = "ErrorInvalidLocalToken"
    ERRORNOLOCALORREMOTEAPPROVAL = "ErrorNoLocalOrRemoteApproval"
    ERRORNOROAMINGAPPROVAL = "ErrorNoRoamingApproval"
    ERRORUNKOWNREMOTETOKEN = "ErrorUnkownRemoteToken"
    WAITINGFORREMOTESTOP = "WaitingForRemoteStop"

    def __str__(self) -> str:
        return str(self.value)

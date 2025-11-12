from enum import Enum


class AuthorizationResultDtoReason(str, Enum):
    APPROVEDBYALLOWANY = "ApprovedByAllowAny"
    APPROVEDBYAUTHREQUEST = "ApprovedByAuthRequest"
    APPROVEDBYLOCALTOKEN = "ApprovedByLocalToken"
    APPROVEDBYREMOTE = "ApprovedByRemote"
    APPROVEDBYROAMINGPARTNER = "ApprovedByRoamingPartner"
    ERRORINTERNALPROBLEM = "ErrorInternalProblem"
    ERRORINVALIDLOCALTOKEN = "ErrorInvalidLocalToken"
    ERRORNOLOCALORREMOTEAPPROVAL = "ErrorNoLocalOrRemoteApproval"
    ERRORNOROAMINGAPPROVAL = "ErrorNoRoamingApproval"
    ERRORUNKOWNREMOTETOKEN = "ErrorUnkownRemoteToken"
    WAITINGFORAUTHORIZATIONRESPONSE = "WaitingForAuthorizationResponse"
    WAITINGFORHUBJECTRESPONSE = "WaitingForHubjectResponse"
    WAITINGFOROCPIRESPONSE = "WaitingForOcpiResponse"
    WAITINGFORREMOTESTOP = "WaitingForRemoteStop"

    def __str__(self) -> str:
        return str(self.value)

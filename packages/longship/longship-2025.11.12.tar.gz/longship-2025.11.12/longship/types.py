from enum import Enum
from typing import Optional, Union

import attr

from longship_api_client.models.chargepoint_dto_connectivity_status import (
    ChargepointDtoConnectivityStatus,
)
from longship_api_client.models.connector_operational_status_dto_operational_status import (
    ConnectorOperationalStatusDtoOperationalStatus,
)


class WebhookPayloadType(str, Enum):
    ChargePointBooted = "ChargePointBooted"
    OperationalStatusChanged = "OperationalStatusChanged"
    ConnectivityStatusChanged = "ConnectivityStatusChanged"
    SessionStart = "SessionStart"
    SessionUpdate = "SessionUpdate"
    SessionStop = "SessionStop"
    CDRCreated = "CdrCreated"
    LocationCreated = "LocationCreated"
    LocationUpdated = "LocationUpdated"
    MSPInvoiceProposalStatus = "MspInvoiceProposalStatus"
    Ping = "Ping"

    def __str__(self) -> str:
        return str(self.value)


class RegistrationStatusType(str, Enum):
    Accepted = "Accepted"
    Pending = "Pending"

    def __str__(self) -> str:
        return str(self.value)


@attr.s(auto_attribs=True)
class ChargePointBootedData:
    registrationstatus: RegistrationStatusType


@attr.s(auto_attribs=True)
class OperationalStatusChangedData:
    status: ConnectorOperationalStatusDtoOperationalStatus
    errorcode: str
    connectornumber: int
    statussource: str
    locationid: Optional[str] = attr.ib(default=None)
    evseid: Optional[str] = attr.ib(default=None)
    vendorid: Optional[str] = attr.ib(default=None)
    vendorerrorcode: Optional[str] = attr.ib(default=None)


@attr.s(auto_attribs=True)
class ConnectivityStatusChangedData:
    # TODO: Longship uses uppercase for the status, but the webhook response uses CamelCase
    status: ChargepointDtoConnectivityStatus


@attr.s(auto_attribs=True)
class BaseSessionData:
    chargepointid: str
    connectornumber: int
    transactionid: str

@attr.s(auto_attribs=True)
class SessionStartData(BaseSessionData):
    locationid: Optional[str] = attr.ib(default=None)
    evseid: Optional[str] = attr.ib(default=None)
    stateofcharge: Optional[float] = attr.ib(default=None)


@attr.s(auto_attribs=True)
class SessionUpdateData(BaseSessionData):
    totalenergyinkwh: float
    totalduration: str
    totalcosts: float
    locationid: Optional[str] = attr.ib(default=None)
    evseid: Optional[str] = attr.ib(default=None)
    stateofcharge: Optional[float] = attr.ib(default=None)


@attr.s(auto_attribs=True)
class SessionStopData(SessionUpdateData):
    locationid: Optional[str] = attr.ib(default=None)
    evseid: Optional[str] = attr.ib(default=None)
    stateofcharge: Optional[float] = attr.ib(default=None)


@attr.s(auto_attribs=True)
class CDRCreatedData:
    chargepointid: str
    connectornumber: int
    totalenergyinkwh: float
    totalduration: str
    totalcosts: float
    transactionid: str
    locationid: Optional[str] = attr.ib(default=None)
    evseid: Optional[str] = attr.ib(default=None)


@attr.s(auto_attribs=True)
class LocationCreatedData:
    pass


@attr.s(auto_attribs=True)
class LocationUpdatedData:
    pass


@attr.s(auto_attribs=True)
class MSPInvoiceProposalStatusData:
    pass


@attr.s(auto_attribs=True)
class PingData:
    pass


@attr.s(auto_attribs=True)
class WebhookPayload:
    specversion: str
    id: str
    type: WebhookPayloadType
    subject: str
    time: str
    source: str
    datacontenttype: str
    data: Union[
        ChargePointBootedData,
        OperationalStatusChangedData,
        ConnectivityStatusChangedData,
        SessionStartData,
        SessionUpdateData,
        SessionStopData,
        CDRCreatedData,
        LocationCreatedData,
        LocationUpdatedData,
        MSPInvoiceProposalStatusData,
        PingData,
    ]

    def _filter_and_create_data(self, data_class):
        """Helper method to filter data and create the appropriate data class instance."""
        if isinstance(self.data, dict):
            field_names = {field.name for field in attr.fields(data_class)}
            filtered_data = {k: v for k, v in self.data.items() if k in field_names}
            return data_class(**filtered_data)
        else:
            # If data is already an instance of the correct class, return it as is
            if isinstance(self.data, data_class):
                return self.data
            # Otherwise, try to create a new instance (this might fail for required fields)
            return data_class(**self.data)

    def __attrs_post_init__(self):
        if self.type == WebhookPayloadType.ChargePointBooted:
            self.data = self._filter_and_create_data(ChargePointBootedData)
        elif self.type == WebhookPayloadType.OperationalStatusChanged:
            self.data = self._filter_and_create_data(OperationalStatusChangedData)
        elif self.type == WebhookPayloadType.ConnectivityStatusChanged:
            if isinstance(self.data, dict):
                self.data["status"] = self.data["status"].upper()
            self.data = self._filter_and_create_data(ConnectivityStatusChangedData)
        elif self.type == WebhookPayloadType.SessionStart:
            self.data = self._filter_and_create_data(SessionStartData)
        elif self.type == WebhookPayloadType.SessionUpdate:
            self.data = self._filter_and_create_data(SessionUpdateData)
        elif self.type == WebhookPayloadType.SessionStop:
            self.data = self._filter_and_create_data(SessionStopData)
        elif self.type == WebhookPayloadType.CDRCreated:
            self.data = self._filter_and_create_data(CDRCreatedData)
        elif self.type == WebhookPayloadType.LocationCreated:
            self.data = self._filter_and_create_data(LocationCreatedData)
        elif self.type == WebhookPayloadType.LocationUpdated:
            self.data = self._filter_and_create_data(LocationUpdatedData)
        elif self.type == WebhookPayloadType.MSPInvoiceProposalStatus:
            self.data = self._filter_and_create_data(MSPInvoiceProposalStatusData)
        elif self.type == WebhookPayloadType.Ping:
            self.data = self._filter_and_create_data(PingData)

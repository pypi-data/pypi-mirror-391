import asyncio
import json
from datetime import datetime
from typing import List
from urllib.parse import parse_qs, urlsplit

from longship.errors import ChargepointNotFoundError, CompositeScheduleNotFoundError
from longship_api_client import Client
from longship_api_client.api.chargepoint_status import (
    chargepoint_status_get,
    get_all_chargepointstatus,
)
from longship_api_client.api.chargepoints import (
    chargepoint_get,
    get_all_chargepointmessages,
)
from longship_api_client.api.commands import (
    send_get_composite_schedule_request,
    send_set_charging_profile_request,
)
from longship_api_client.api.sessions import get_all_sessions
from longship_api_client.models import (
    GetCompositeScheduleRequest,
    SetChargingProfileRequest,
)
from longship_api_client.models.chargepoint_dto import ChargepointDto
from longship_api_client.models.chargepoint_status_dto import ChargepointStatusDto
from longship_api_client.models.charging_schedule import ChargingSchedule
from longship_api_client.models.charging_schedule_charging_rate_unit import (
    ChargingScheduleChargingRateUnit,
)
from longship_api_client.models.charging_schedule_period import ChargingSchedulePeriod
from longship_api_client.models.cs_charging_profiles import CsChargingProfiles
from longship_api_client.models.cs_charging_profiles_charging_profile_kind import (
    CsChargingProfilesChargingProfileKind,
)
from longship_api_client.models.cs_charging_profiles_charging_profile_purpose import (
    CsChargingProfilesChargingProfilePurpose,
)
from longship_api_client.models.get_composite_schedule_request_charging_rate_unit import (
    GetCompositeScheduleRequestChargingRateUnit,
)
from longship_api_client.models.message_log_dto import MessageLogDto
from longship_api_client.models.session_dto import SessionDto


class Longship:
    instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls.instance, cls):
            cls.instance = object.__new__(cls)
        return cls.instance

    def __init__(self, url: str, apiKey: str, ocpKey: str) -> None:
        self._client = Client(base_url=url).with_headers(
            {"x-api-key": apiKey, "Ocp-Apim-Subscription-Key": ocpKey}
        )

    async def get_composite_schedule(
        self,
        chargepoint_id: str,
        connector_id=0,
        duration=3600,
        unit=GetCompositeScheduleRequestChargingRateUnit.W,
    ) -> ChargingSchedule:
        request = GetCompositeScheduleRequest(
            connector_id=connector_id, duration=duration, charging_rate_unit=unit
        )
        response = await send_get_composite_schedule_request.asyncio_detailed(
            id=chargepoint_id, json_body=request, client=self._client
        )
        if response.status_code == 404:
            raise ChargepointNotFoundError

        query = urlsplit(response.headers["location"]).query
        params = parse_qs(query)
        message_id = params["messageId"]
        await asyncio.sleep(1)

        response = await self.get_messages(
            chargepoint_id, response_only=True, message_id=message_id
        )
        if response.status_code != 200:
            raise Exception("Failed to load the messages")
        content = json.loads(response.content)
        if len(content) == 0:
            # TODO: Retry
            raise Exception("No response from the charger yet")
        payload = json.loads(content[0]["payload"])

        try:
            schedule = ChargingSchedule.from_dict(payload[2]["chargingSchedule"])
            return schedule
        except KeyError:
            raise CompositeScheduleNotFoundError

    def _create_charging_schedule(
        self, max_power: int, min_power: int = 1000, number_of_phases: int = 3
    ):
        period = ChargingSchedulePeriod(
            start_period=0, limit=max_power, number_phases=number_of_phases
        )
        schedule = ChargingSchedule(
            start_schedule=datetime.fromisoformat("2000-01-01T00:00:00"),
            charging_rate_unit=ChargingScheduleChargingRateUnit.W,
            min_charging_rate=min_power,
            charging_schedule_period=[period],
        )
        return schedule

    async def set_charge_point_max_power(
        self,
        chargepoint_id: str,
        max_power: int,
        min_power: int = 1000,
        number_of_phases: int = 3,
    ):
        schedule = self._create_charging_schedule(
            max_power, min_power, number_of_phases
        )
        profiles = CsChargingProfiles(
            charging_profile_id=1,
            stack_level=1,
            charging_profile_purpose=CsChargingProfilesChargingProfilePurpose.CHARGEPOINTMAXPROFILE,
            charging_profile_kind=CsChargingProfilesChargingProfileKind.ABSOLUTE,
            charging_schedule=schedule,
        )
        request = SetChargingProfileRequest(
            connector_id=0, cs_charging_profiles=profiles
        )
        return await send_set_charging_profile_request.asyncio_detailed(
            id=chargepoint_id, json_body=request, client=self._client
        )

    async def set_transaction_max_power(
        self,
        chargepoint_id: str,
        connector_id: int,
        transaction_id: int,
        max_power: int,
        min_power: int = 1000,
        number_of_phases: int = 3,
    ):
        schedule = self._create_charging_schedule(
            max_power, min_power, number_of_phases
        )
        profiles = CsChargingProfiles(
            charging_profile_id=2,
            stack_level=2,
            transaction_id=transaction_id,
            charging_profile_purpose=CsChargingProfilesChargingProfilePurpose.TXPROFILE,
            charging_profile_kind=CsChargingProfilesChargingProfileKind.ABSOLUTE,
            charging_schedule=schedule,
        )
        request = SetChargingProfileRequest(
            connector_id=connector_id, cs_charging_profiles=profiles
        )
        return await send_set_charging_profile_request.asyncio_detailed(
            id=chargepoint_id, json_body=request, client=self._client
        )

    async def get_messages(
        self,
        chargepoint_id: str,
        response_only=False,
        message_id=None,
        message_types=None,
    ) -> List[MessageLogDto]:
        return await get_all_chargepointmessages.asyncio_detailed(
            id=chargepoint_id,
            response_only=response_only,
            message_id=message_id,
            message_types=message_types,
            client=self._client,
        )

    async def get_chargepoint(self, chargepoint_id: str) -> ChargepointDto:
        response = await chargepoint_get.asyncio_detailed(
            id=chargepoint_id, client=self._client
        )
        return response.parsed

    async def list_chargepoint_statuses(
        self, skip: int = None, take: int = None
    ) -> ChargepointStatusDto:
        response = await get_all_chargepointstatus.asyncio_detailed(
            skip=skip, take=take, client=self._client
        )
        return response.parsed

    async def get_chargepoint_status(self, chargepoint_id: str) -> ChargepointStatusDto:
        response = await chargepoint_status_get.asyncio_detailed(
            id=chargepoint_id, client=self._client
        )
        return response.parsed

    async def get_sessions(
        self, chargepoint_id=None, connector_number=None, running_only=True
    ) -> List[SessionDto]:
        response = await get_all_sessions.asyncio_detailed(
            chargepoint_id=chargepoint_id,
            connector_number=connector_number,
            running_only=running_only,
            client=self._client,
        )
        return response.parsed

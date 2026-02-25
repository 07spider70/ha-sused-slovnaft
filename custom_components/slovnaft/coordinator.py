"""DataUpdateCoordinators for the Sused Slovnaft integration."""
import logging
from datetime import timedelta
from typing import Dict

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SlovnaftApiClient, SlovnaftApiError
from .const import DOMAIN
from .models import StationAirQuality, CalendarDayStatus

_LOGGER = logging.getLogger(__name__)

class SlovnaftEnvUpdateCoordinator(DataUpdateCoordinator[Dict[str, StationAirQuality]]):
    def __init__(self, hass: HomeAssistant, client: SlovnaftApiClient, update_interval_seconds: int, entry: ConfigEntry) -> None:
        self.client = client
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_environment",
            update_interval=timedelta(seconds=update_interval_seconds),
            config_entry=entry,
        )

    async def _async_update_data(self) -> Dict[str, StationAirQuality]:
        try:
            _LOGGER.debug("Updating StationAirQuality data")
            return await self.client.get_environment()
        except SlovnaftApiError as err:
            _LOGGER.exception("Failed to update environment data: %s", err)
            raise UpdateFailed(f"Environment API error: {err}") from err

class SlovnaftCalendarUpdateCoordinator(DataUpdateCoordinator[Dict[int, CalendarDayStatus]]):
    def __init__(self, hass: HomeAssistant, client: SlovnaftApiClient, update_interval_seconds: int, entry: ConfigEntry) -> None:
        self.client = client
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_calendar",
            update_interval=timedelta(seconds=update_interval_seconds),
            config_entry=entry,
        )

    async def _async_update_data(self) -> Dict[int, CalendarDayStatus]:
        try:
            _LOGGER.debug("Updating Calendar data")
            return await self.client.get_calendar()
        except SlovnaftApiError as err:
            _LOGGER.exception("Failed to update calendar data: %s", err)
            raise UpdateFailed(f"Calendar API error: {err}") from err
"""DataUpdateCoordinators for the Sused Slovnaft integration."""
import logging
from datetime import timedelta
from typing import Dict

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SlovnaftApiClient, SlovnaftApiError
from .const import DOMAIN
from .models import StationAirQuality, CalendarData

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
            result = await self.client.get_environment()
            _LOGGER.debug(
                "Environment update complete: %d stations (%s)",
                len(result),
                ", ".join(result.keys()),
            )
            return result
        except SlovnaftApiError as err:
            raise UpdateFailed(f"Environment API error: {err}") from err

class SlovnaftCalendarUpdateCoordinator(DataUpdateCoordinator[CalendarData]):
    def __init__(self, hass: HomeAssistant, client: SlovnaftApiClient, update_interval_seconds: int, entry: ConfigEntry) -> None:
        self.client = client
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_calendar",
            update_interval=timedelta(seconds=update_interval_seconds),
            config_entry=entry,
        )

    async def _async_update_data(self) -> CalendarData:
        try:
            _LOGGER.debug("Updating Calendar data")
            result = await self.client.get_calendar()
            _LOGGER.debug(
                "Calendar update complete: %d days, notes available for months: %s",
                len(result.days),
                [k for k, v in result.notes_by_month.items() if v],
            )
            return result
        except SlovnaftApiError as err:
            raise UpdateFailed(f"Calendar API error: {err}") from err
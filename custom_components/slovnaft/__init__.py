"""The Sused Slovnaft integration."""
import logging

from dataclasses import dataclass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SlovnaftApiClient
from .const import ENV_ENDPOINT_DEFAULT_INTERVAL_MIN, CALENDAR_ENDPOINT_DEFAULT_INTERVAL_HOURS

from .coordinator import SlovnaftEnvUpdateCoordinator, SlovnaftCalendarUpdateCoordinator

PLATFORMS = ["sensor", "binary_sensor", "calendar"]

_LOGGER = logging.getLogger(__name__)

@dataclass
class SlovnaftData:
    """Runtime data definition for Sused Slovnaft."""
    env_coordinator: SlovnaftEnvUpdateCoordinator | None
    calendar_coordinator: SlovnaftCalendarUpdateCoordinator | None

type SlovnaftConfigEntry = ConfigEntry[SlovnaftData]

async def async_setup_entry(hass: HomeAssistant, entry: SlovnaftConfigEntry) -> bool:
    """Set up Sused Slovnaft from a config entry."""
    session = async_get_clientsession(hass)
    client = SlovnaftApiClient(session=session)

    env_coord = None
    cal_coord = None

    if entry.data.get("enable_env", True):
        env_interval = entry.data.get("env_interval", ENV_ENDPOINT_DEFAULT_INTERVAL_MIN) * 60
        _LOGGER.debug(f"Setting up env update coordinator with interval {env_interval} seconds")
        env_coord = SlovnaftEnvUpdateCoordinator(hass, client, env_interval, entry)
        await env_coord.async_config_entry_first_refresh()

    if entry.data.get("enable_calendar", True):
        cal_interval = entry.data.get("calendar_interval", CALENDAR_ENDPOINT_DEFAULT_INTERVAL_HOURS) * 3600
        _LOGGER.debug(f"Setting up calendar update coordinator with interval {cal_interval} seconds")
        cal_coord = SlovnaftCalendarUpdateCoordinator(hass, client, cal_interval, entry)
        await cal_coord.async_config_entry_first_refresh()

    entry.runtime_data = SlovnaftData(
        env_coordinator=env_coord,
        calendar_coordinator=cal_coord
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: SlovnaftConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old configuration entries to the new format."""
    _LOGGER.debug("Migrating configuration from version %s", config_entry.version)

    if config_entry.version == 1:
        new_data = {**config_entry.data}

        if "calendar_interval" in new_data:
            val = str(new_data["calendar_interval"])
            # Fallback to "24" (1 day) if the old value isn't in our new strict dropdown list
            if val not in ["12", "24", "72", "168"]:
                val = "24"
                _LOGGER.warning("Old calendar_interval not in allowed options. Defaulting to 24.")
            new_data["calendar_interval"] = val

        # Update the entry with the new data and the new version number
        hass.config_entries.async_update_entry(
            config_entry,
            data=new_data,
            version=2
        )

    _LOGGER.info("Migration to version %s successful", config_entry.version)
    return True
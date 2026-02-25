"""The Sused Slovnaft integration."""
from dataclasses import dataclass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SlovnaftApiClient
from .const import DOMAIN
from .coordinator import SlovnaftEnvUpdateCoordinator, SlovnaftCalendarUpdateCoordinator

PLATFORMS = ["sensor", "binary_sensor", "calendar"]

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
        env_interval = entry.data.get("env_interval", 10) * 60
        env_coord = SlovnaftEnvUpdateCoordinator(hass, client, env_interval, entry)
        await env_coord.async_config_entry_first_refresh()

    if entry.data.get("enable_calendar", True):
        cal_interval = entry.data.get("calendar_interval", 12) * 3600
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
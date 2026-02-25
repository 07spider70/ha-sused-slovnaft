"""Config flow for Sused Slovnaft integration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SlovnaftApiClient
from .const import DOMAIN, STATIONS

class SlovnaftConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sused Slovnaft."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial configuration step."""

        # Enforce unique config entry (Only 1 installation allowed)
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        errors = {}

        if user_input is not None:
            if not user_input.get("enable_env") and not user_input.get("enable_calendar"):
                errors["base"] = "no_api_selected"
            else:
                # Test API Connection before completing the setup
                session = async_get_clientsession(self.hass)
                client = SlovnaftApiClient(session=session)
                try:
                    if user_input.get("enable_env"):
                        await client.get_environment()
                    if user_input.get("enable_calendar"):
                        await client.get_calendar()
                except Exception:
                    errors["base"] = "cannot_connect"
                else:
                    return self.async_create_entry(title="Sused Slovnaft", data=user_input)

        station_options = [
            selector.SelectOptionDict(value=station_id, label=name)
            for station_id, name in STATIONS.items()
        ]

        data_schema = vol.Schema({
            vol.Required("enable_env", default=True): bool,
            vol.Required("env_interval", default=10): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
            vol.Required("enable_calendar", default=True): bool,
            vol.Required("calendar_interval", default=12): vol.All(vol.Coerce(int), vol.Range(min=1, max=168)),
            vol.Required("stations", default=list(STATIONS.keys())): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=station_options, multiple=True, mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        })

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)
"""Config flow for Sused Slovnaft integration."""
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SlovnaftApiClient, SlovnaftApiError
from .const import DOMAIN, STATIONS
from .const import ENV_ENDPOINT_DEFAULT_INTERVAL_MIN, ENV_ENDPOINT_MIN_INTERVAL_MIN, ENV_ENDPOINT_MAX_INTERVAL_MIN, CALENDAR_ENDPOINT_DEFAULT_INTERVAL_HOURS, CALENDAR_ENDPOINT_MIN_INTERVAL_HOURS, CALENDAR_ENDPOINT_MAX_INTERVAL_HOURS

_LOGGER = logging.getLogger(__name__)

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
                _LOGGER.debug("No API selected")
            else:
                # Test API Connection before completing the setup
                session = async_get_clientsession(self.hass)
                client = SlovnaftApiClient(session=session)
                try:
                    if user_input.get("enable_env"):
                        await client.get_environment()
                    if user_input.get("enable_calendar"):
                        await client.get_calendar()
                except SlovnaftApiError:
                    _LOGGER.error("API connection failed during config flow: %s", user_input)
                    errors["base"] = "cannot_connect"
                else:
                    return self.async_create_entry(title="Sused Slovnaft", data=user_input)

        station_options = [
            selector.SelectOptionDict(value=station_id, label=name)
            for station_id, name in STATIONS.items()
        ]

        data_schema = vol.Schema({
            vol.Required("enable_env", default=True): bool,
            vol.Required("env_interval", default=ENV_ENDPOINT_DEFAULT_INTERVAL_MIN):
                vol.All(vol.Coerce(int), vol.Range(min=ENV_ENDPOINT_MIN_INTERVAL_MIN,
                                                   max=ENV_ENDPOINT_MAX_INTERVAL_MIN)),
            vol.Required("enable_calendar", default=True): bool,
            vol.Required("calendar_interval", default=CALENDAR_ENDPOINT_DEFAULT_INTERVAL_HOURS):
                vol.All(vol.Coerce(int), vol.Range(min=CALENDAR_ENDPOINT_MIN_INTERVAL_HOURS,
                                                   max=CALENDAR_ENDPOINT_MAX_INTERVAL_HOURS)),
            vol.Required("stations", default=list(STATIONS.keys())): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=station_options, multiple=True, mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        })

        return self.async_show_form(step_id="user",data_schema=data_schema, errors=errors)

    async def async_step_reconfigure(self, user_input=None):
        """Handle the reconfiguration of the integration."""
        entry = self._get_reconfigure_entry()
        errors = {}

        if user_input is not None:
            # We must validate the API connection again in case they turned it back on!
            if not user_input.get("enable_env") and not user_input.get("enable_calendar"):
                errors["base"] = "no_api_selected"
            else:
                session = async_get_clientsession(self.hass)
                client = SlovnaftApiClient(session)
                try:
                    if user_input.get("enable_env"):
                        await client.get_environment()
                    if user_input.get("enable_calendar"):
                        await client.get_calendar()
                except SlovnaftApiError:
                    _LOGGER.error("API connection failed during config flow: %s", user_input)
                    errors["base"] = "cannot_connect"
                else:
                    # It updates the saved data and reboots the integration instantly.
                    return self.async_update_reload_and_abort(
                        entry,
                        data=user_input,
                        reason="reconfigure_successful"
                    )

        # Pre-fill the dropdown options
        station_options = [
            selector.SelectOptionDict(value=station_id, label=name)
            for station_id, name in STATIONS.items()
        ]

        # Use the existing entry.data to set the default values so the user sees their current settings!
        data_schema = vol.Schema({
            vol.Required("enable_env", default=entry.data.get("enable_env", True)): bool,
            vol.Required("env_interval", default=entry.data.get("env_interval", ENV_ENDPOINT_DEFAULT_INTERVAL_MIN)):
                vol.All(vol.Coerce(int),
                        vol.Range(min=ENV_ENDPOINT_MIN_INTERVAL_MIN,
                            max=ENV_ENDPOINT_MAX_INTERVAL_MIN)),
            vol.Required("enable_calendar", default=entry.data.get("enable_calendar", True)): bool,
            vol.Required("calendar_interval", default=entry.data.get("calendar_interval", CALENDAR_ENDPOINT_DEFAULT_INTERVAL_HOURS)):
                vol.All(vol.Coerce(int),
                    vol.Range(min=CALENDAR_ENDPOINT_MIN_INTERVAL_HOURS,
                        max=CALENDAR_ENDPOINT_MAX_INTERVAL_HOURS)),
            vol.Required("stations",
                         default=entry.data.get("stations", list(STATIONS.keys()))): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=station_options,
                    multiple=True,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        })

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=data_schema,
            errors=errors
        )
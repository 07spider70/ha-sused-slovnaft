"""Test the Sused Slovnaft config flow."""
import pytest
from unittest.mock import patch
from homeassistant import config_entries
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.slovnaft.const import DOMAIN
from custom_components.slovnaft.config_flow import SlovnaftConfigFlow
from custom_components.slovnaft.api import SlovnaftApiError

@pytest.fixture(autouse=True)
def bypass_integration_loader():
    """Bypass the HA file loader and inject the Config Flow handler directly."""
    with patch("homeassistant.config_entries._load_integration"), \
         patch.dict(config_entries.HANDLERS, {DOMAIN: SlovnaftConfigFlow}):
        yield

@pytest.mark.asyncio
async def test_successful_config_flow(hass):
    """Test we show the form and create an entry when user fills it out."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == "form"
    assert result["errors"] == {}

    with patch("custom_components.slovnaft.config_flow.SlovnaftApiClient.get_environment"), \
         patch("custom_components.slovnaft.config_flow.SlovnaftApiClient.get_calendar"), \
         patch.object(hass.config_entries, "async_setup", return_value=True) as mock_setup:

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "enable_env": True,
                "env_interval": 15,
                "enable_calendar": True,
                "calendar_interval": "24",
                "stations": ["116"],
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] == "create_entry"
    assert result2["title"] == "Sused Slovnaft"
    assert result2["data"]["stations"] == ["116"]
    assert mock_setup.call_count == 1

@pytest.mark.asyncio
async def test_form_no_api_selected_error(hass):
    """Test that we throw an error if the user disables everything."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"enable_env": False, "enable_calendar": False, "stations": ["116"]},
    )

    assert result2["type"] == "form"
    assert result2["errors"] == {"base": "no_api_selected"}

@pytest.mark.asyncio
async def test_form_cannot_connect_error(hass):
    """Test we show error when API connection fails."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Use the specific SlovnaftApiError to trigger the failure properly
    with patch("custom_components.slovnaft.config_flow.SlovnaftApiClient.get_environment", side_effect=SlovnaftApiError("API Down")):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"enable_env": True, "env_interval": 15, "enable_calendar": False, "calendar_interval": "24", "stations": ["116"]},
        )

    assert result2["type"] == "form"
    assert result2["errors"] == {"base": "cannot_connect"}

@pytest.mark.asyncio
async def test_reconfigure_flow_success(hass):
    """Test that the reconfiguration flow updates the entry and reloads."""
    entry = MockConfigEntry(
        domain=DOMAIN, title="Sused Slovnaft",
        data={"enable_env": True, "env_interval": 10, "enable_calendar": True, "calendar_interval": "12", "stations": ["116"]},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_RECONFIGURE, "entry_id": entry.entry_id}
    )

    with patch("custom_components.slovnaft.config_flow.SlovnaftApiClient.get_environment"), \
         patch("custom_components.slovnaft.config_flow.SlovnaftApiClient.get_calendar"), \
         patch("homeassistant.config_entries.ConfigEntries.async_reload", return_value=True) as mock_reload:

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"enable_env": True, "env_interval": 45, "enable_calendar": True, "calendar_interval": "12", "stations": ["116", "117"]},
        )
        await hass.async_block_till_done()

    assert result2["type"] == "abort"
    assert result2["reason"] == "reconfigure_successful"
    assert entry.data["env_interval"] == 45
    assert entry.data["stations"] == ["116", "117"]
    assert mock_reload.call_count == 1
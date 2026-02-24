"""Fixtures for Sused Slovnaft testing."""
import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from pytest_homeassistant_custom_component.common import MockConfigEntry
from custom_components.slovnaft.api import SlovnaftApiClient
from custom_components.slovnaft.const import DOMAIN

@pytest.fixture
async def mock_api_client(hass: HomeAssistant):
    session = async_get_clientsession(hass)
    return SlovnaftApiClient(session)

@pytest.fixture
def mock_config_entry():
    return MockConfigEntry(
        domain=DOMAIN,
        title="Sused Slovnaft",
        data={
            "enable_env": True,
            "env_interval": 10,
            "enable_calendar": True,
            "calendar_interval": 12,
            "stations": ["116"],
        },
        entry_id="test_entry_123",
    )
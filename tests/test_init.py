"""Tests for integration setup."""
import pytest
from unittest.mock import patch
from homeassistant.config_entries import ConfigEntryState
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.slovnaft import async_migrate_entry
from custom_components.slovnaft import async_setup_entry, async_unload_entry
from custom_components.slovnaft.const import DOMAIN
from custom_components.slovnaft.models import CalendarData

@pytest.mark.asyncio
async def test_setup_unload_entry(hass, mock_config_entry):
    """Test full integration setup cycle by calling entry point directly."""

    mock_config_entry.add_to_hass(hass)

    mock_config_entry.mock_state(hass, ConfigEntryState.SETUP_IN_PROGRESS)

    empty_calendar = CalendarData(days={}, notes_by_month={})

    with patch("custom_components.slovnaft.api.SlovnaftApiClient.get_calendar", return_value=empty_calendar), \
         patch("custom_components.slovnaft.api.SlovnaftApiClient.get_environment", return_value={}), \
         patch.object(hass.config_entries, "async_forward_entry_setups") as mock_forward:

        assert await async_setup_entry(hass, mock_config_entry)

        assert mock_config_entry.runtime_data.env_coordinator is not None
        assert mock_forward.called

    mock_config_entry.mock_state(hass, ConfigEntryState.LOADED)

    with patch.object(hass.config_entries, "async_unload_platforms", return_value=True) as mock_unload:
        assert await async_unload_entry(hass, mock_config_entry)
        assert mock_unload.called


@pytest.mark.asyncio
async def test_migration_v1_to_v2_successful(hass):
    """Test successful migration when interval is a valid allowed option."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=1,
        data={"calendar_interval": 24, "enable_calendar": True}
    )
    entry.add_to_hass(hass)

    # Run the migration
    assert await async_migrate_entry(hass, entry)

    # Assert version bumped to 2
    assert entry.version == 2
    # Assert integer 24 became string "24"
    assert entry.data["calendar_interval"] == "24"
    assert entry.data["enable_calendar"] is True


@pytest.mark.asyncio
async def test_migration_v1_to_v2_invalid_value(hass):
    """Test migration when interval does not correspond to defined strings."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=1,
        data={"calendar_interval": 42, "enable_calendar": True}
    )
    entry.add_to_hass(hass)

    assert await async_migrate_entry(hass, entry)

    assert entry.version == 2
    # Assert the unsupported integer 42 fell back to the safe default "24"
    assert entry.data["calendar_interval"] == "24"


@pytest.mark.asyncio
async def test_migration_v1_to_v2_missing_key(hass):
    """Test migration when calendar_interval is completely missing from data."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=1,
        # Simulating an old config where maybe only env was set up
        data={"enable_env": True, "env_interval": 15}
    )
    entry.add_to_hass(hass)

    assert await async_migrate_entry(hass, entry)

    assert entry.version == 2
    # Assert it didn't crash and left the data alone if key wasn't there
    assert "calendar_interval" not in entry.data
    assert entry.data["enable_env"] is True
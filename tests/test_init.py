"""Tests for integration setup."""
import pytest
from unittest.mock import patch
from homeassistant.config_entries import ConfigEntryState
from custom_components.slovnaft import async_setup_entry, async_unload_entry

@pytest.mark.asyncio
async def test_setup_unload_entry(hass, mock_config_entry):
    """Test full integration setup cycle by calling entry point directly."""

    mock_config_entry.add_to_hass(hass)

    mock_config_entry.mock_state(hass, ConfigEntryState.SETUP_IN_PROGRESS)

    with patch("custom_components.slovnaft.api.SlovnaftApiClient.get_calendar", return_value={}), \
         patch("custom_components.slovnaft.api.SlovnaftApiClient.get_environment", return_value={}), \
         patch.object(hass.config_entries, "async_forward_entry_setups") as mock_forward:

        assert await async_setup_entry(hass, mock_config_entry)

        assert mock_config_entry.runtime_data.env_coordinator is not None
        assert mock_forward.called

    mock_config_entry.mock_state(hass, ConfigEntryState.LOADED)

    with patch.object(hass.config_entries, "async_unload_platforms", return_value=True) as mock_unload:
        assert await async_unload_entry(hass, mock_config_entry)
        assert mock_unload.called
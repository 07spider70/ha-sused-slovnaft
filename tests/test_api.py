"""Tests for the Slovnaft API client."""
import pytest
from aioresponses import aioresponses
from custom_components.slovnaft.api import (
    SlovnaftConnectionError
)
from custom_components.slovnaft.const import CALENDAR_ENDPOINT

@pytest.mark.asyncio
async def test_get_calendar_success(mock_api_client):
    """Test successful calendar parsing and HTML stripping."""
    with aioresponses() as m:
        # We simulate the API returning messy HTML notes and day data
        m.get(
            f"{CALENDAR_ENDPOINT}/2026-2",
            payload={
                "thisMonth": [{"date": 1771974000, "attributes": {"fire": 1, "smell": 0}}],
                "thisMonthNote": "<p class=\"MsoNormal\">Aktualizácia <b>24. 2. 2026</b></p><br/>"
            }
        )
        result = await mock_api_client.get_calendar()

        # Verify the dates were parsed correctly into the 'days' dictionary
        assert 1771974000 in result.days
        assert result.days[1771974000].fire is True

        # Verify the HTML was cleanly stripped from the note
        assert result.this_month_note == "Aktualizácia 24. 2. 2026"

@pytest.mark.asyncio
async def test_api_connection_error(mock_api_client):
    """Test 500 error handling."""
    with aioresponses() as m:
        m.get(f"{CALENDAR_ENDPOINT}/2026-2", status=500)
        with pytest.raises(SlovnaftConnectionError):
            await mock_api_client.get_calendar()
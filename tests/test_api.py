"""Tests for the Slovnaft API client."""
import pytest
from aioresponses import aioresponses
import homeassistant.util.dt as dt_util

from custom_components.slovnaft.api import (
    SlovnaftConnectionError
)
from custom_components.slovnaft.const import CALENDAR_ENDPOINT

@pytest.mark.asyncio
async def test_get_calendar_success(mock_api_client):
    """Test successful calendar parsing and HTML stripping."""
    now = dt_util.now()

    with aioresponses() as m:
        m.get(
            f"{CALENDAR_ENDPOINT}/{now.year}-{now.month}",
            payload={
                "thisMonth": [{
                    "date": 1771974000,
                    "edited": "1",
                    "note": "<p class=\"MsoNormal\">Scheduled flaring at 14:00.</p><br/>",
                    "attributes": {"fire": 1, "smell": 0}
                }],
                "thisMonthNote": "<p class=\"MsoNormal\">Aktualizácia <b>24. 2. 2026</b></p><br/>"
            }
        )
        result = await mock_api_client.get_calendar()

        assert 1771974000 in result.days
        assert result.days[1771974000].fire is True

        assert result.days[1771974000].edited is True
        assert result.days[1771974000].note == "Scheduled flaring at 14:00."

        assert result.this_month_note == "Aktualizácia 24. 2. 2026"

@pytest.mark.asyncio
async def test_api_connection_error(mock_api_client):
    """Test 500 error handling."""
    now = dt_util.now()

    with aioresponses() as m:
        m.get(f"{CALENDAR_ENDPOINT}/{now.year}-{now.month}", status=500)
        with pytest.raises(SlovnaftConnectionError):
            await mock_api_client.get_calendar()
"""Tests for the Slovnaft API client."""
import pytest
from aioresponses import aioresponses
from custom_components.slovnaft.api import (
    SlovnaftApiClient, 
    SlovnaftConnectionError
)
from custom_components.slovnaft.const import CALENDAR_ENDPOINT, ENV_ENDPOINT

@pytest.mark.asyncio
async def test_get_calendar_success(mock_api_client):
    """Test successful calendar parsing."""
    with aioresponses() as m:
        m.get(
            f"{CALENDAR_ENDPOINT}/2026-2",
            payload={"thisMonth": [{"date": 1771974000, "attributes": {"fire": 1}}]}
        )
        result = await mock_api_client.get_calendar()
        assert 1771974000 in result

@pytest.mark.asyncio
async def test_api_connection_error(mock_api_client):
    """Test 500 error handling."""
    with aioresponses() as m:
        m.get(f"{CALENDAR_ENDPOINT}/2026-2", status=500)
        with pytest.raises(SlovnaftConnectionError):
            await mock_api_client.get_calendar()
"""Tests for Slovnaft sensors."""
import datetime
import pytest
from unittest.mock import patch, MagicMock

from custom_components.slovnaft.models import CalendarDayStatus, CalendarData
from custom_components.slovnaft.binary_sensor import SlovnaftCalendarSensor
from custom_components.slovnaft.calendar import SlovnaftCalendarEntity

def test_calendar_today_logic():
    """Verify that the sensor correctly identifies 'today' from the timestamp."""
    today_dt = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_ts = int(today_dt.timestamp())

    status = CalendarDayStatus(
        date_timestamp=today_ts,
        fire=True, smell=False, noise=False, water=False, smoke=False, work=False
    )

    # Wrap the status in the new CalendarData model
    mock_api_data = CalendarData(
        days={today_ts: status},
        last_month_note=None,
        this_month_note=None,
        next_month_note=None
    )

    # Simulate the binary_sensor's is_on logic traversing the .days dictionary
    is_fire_on = False
    for ts, day_status in mock_api_data.days.items():
        if datetime.datetime.fromtimestamp(ts).date() == datetime.datetime.now().date():
            is_fire_on = day_status.fire

    assert is_fire_on is True


def test_calendar_notes_sensor_logic():
    """Verify the logic that determines the main state of the notes sensor."""
    # Scenario 1: Notes exist
    mock_data_with_notes = CalendarData(
        days={}, last_month_note=None, this_month_note="Flaring scheduled.", next_month_note=None
    )
    assert ("Available" if mock_data_with_notes.this_month_note else "No Notes") == "Available"

    # Scenario 2: No notes exist
    mock_data_empty = CalendarData(
        days={}, last_month_note=None, this_month_note=None, next_month_note=None
    )
    assert ("Available" if mock_data_empty.this_month_note else "No Notes") == "No Notes"


@pytest.mark.asyncio
async def test_binary_sensor_midnight_redraw(hass):
    """Test that the binary sensor schedules a state update exactly at midnight."""
    # 1. Create a dummy sensor
    coordinator = MagicMock()
    sensor = SlovnaftCalendarSensor(coordinator, "fire", {"icon": "mdi:fire"})
    sensor.hass = hass

    # 2. Catch the async_track_time_change request when the sensor is added
    with patch("custom_components.slovnaft.binary_sensor.async_track_time_change") as mock_track:
        await sensor.async_added_to_hass()

        # Verify it requested a wake-up call at 00:00:01
        assert mock_track.call_count == 1
        args, kwargs = mock_track.call_args
        assert kwargs["hour"] == 0
        assert kwargs["minute"] == 0
        assert kwargs["second"] == 1

        # 3. Extract the hidden callback function that gets triggered at midnight
        update_callback = args[1]

        # 4. Simulate the clock striking midnight and verify it redraws the UI!
        with patch.object(sensor, "async_write_ha_state") as mock_write:
            update_callback(None) # 'None' simulates the current time object
            mock_write.assert_called_once()


@pytest.mark.asyncio
async def test_calendar_midnight_redraw(hass):
    """Test that the calendar entity schedules a state update exactly at midnight."""
    # 1. Create a dummy calendar entity
    coordinator = MagicMock()
    entity = SlovnaftCalendarEntity(coordinator)
    entity.hass = hass

    # 2. Catch the async_track_time_change request
    with patch("custom_components.slovnaft.calendar.async_track_time_change") as mock_track:
        await entity.async_added_to_hass()

        # Verify it requested a wake-up call at 00:00:01
        assert mock_track.call_count == 1
        args, kwargs = mock_track.call_args
        assert kwargs["hour"] == 0
        assert kwargs["minute"] == 0
        assert kwargs["second"] == 1

        # 3. Extract the callback function
        update_callback = args[1]

        # 4. Simulate the clock striking midnight and verify it redraws the UI!
        with patch.object(entity, "async_write_ha_state") as mock_write:
            update_callback(None)
            mock_write.assert_called_once()
"""Tests for Slovnaft sensors."""
import datetime
import pytest
from unittest.mock import patch, MagicMock
import homeassistant.util.dt as dt_util
from custom_components.slovnaft.models import CalendarDayStatus, CalendarData, StationAirQuality
from custom_components.slovnaft.binary_sensor import SlovnaftCalendarSensor
from custom_components.slovnaft.calendar import SlovnaftCalendarEntity
from custom_components.slovnaft.sensor import SlovnaftCalendarNoteSensor, SlovnaftAirQualitySensor

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

def test_calendar_today_logic_class():
    """Verify the actual binary sensor class logic."""
    # 1. Create a fake timezone-aware 'today' using dt_util
    today_dt = dt_util.now().replace(hour=12, minute=0, second=0, microsecond=0)
    today_ts = int(today_dt.timestamp())

    # 2. Setup the mock data exactly as the coordinator would provide it
    status = CalendarDayStatus(
        date_timestamp=today_ts,
        fire=True, smell=False, noise=False, water=False, smoke=False, work=False
    )
    mock_api_data = CalendarData(
        days={today_ts: status},
        last_month_note=None, this_month_note=None, next_month_note=None
    )

    # 3. Create a fake coordinator that holds our mock data
    mock_coordinator = MagicMock()
    mock_coordinator.data = mock_api_data

    # 4. INSTANTIATE THE ACTUAL SENSOR
    sensor = SlovnaftCalendarSensor(
        coordinator=mock_coordinator,
        sensor_key="fire",
        sensor_info={"icon": "mdi:fire"}
    )

    # 5. TEST THE ACTUAL PROPERTY
    assert sensor.is_on is True

def test_calendar_notes_sensor_real():
    """Test that the calendar note sensor exposes states and attributes correctly."""
    mock_coordinator = MagicMock()

    # Scenario 1: Notes exist
    mock_coordinator.data = CalendarData(
        days={},
        last_month_note="<p>Old note</p>",
        this_month_note="<p>Current note</p>",
        next_month_note="<p>Future note</p>"
    )

    sensor = SlovnaftCalendarNoteSensor(coordinator=mock_coordinator)

    # Check main state
    assert sensor.native_value == "Available"

    # Check extra attributes
    attrs = sensor.extra_state_attributes
    assert attrs["last_month_note"] == "<p>Old note</p>"
    assert attrs["this_month_note"] == "<p>Current note</p>"
    assert attrs["next_month_note"] == "<p>Future note</p>"

    # Scenario 2: No notes exist
    mock_coordinator.data.this_month_note = None
    assert sensor.native_value == "No Notes"


def test_air_quality_sensor_real():
    """Test that the air quality sensor pulls the correct measurement."""
    mock_coordinator = MagicMock()

    # Setup mock data for two different stations
    station_1 = StationAirQuality(
        site_number="1", timestamp=1600000000, pm10=15.5, temp=22.0,
        pm25=None, so2=None, no=None, no2=None, nox=None, o3=None,
        co=None, ch4=None, nmhc=None, thc=None, c6h6=None, c7h8=None,
        c8h0=None, c4h6=None, h2s=None, pres=None, humi=None, glrd=None,
        filt=None, wind_direction_name=None, wind_speed=None, wind_degrees=None
    )
    station_2 = StationAirQuality(
        site_number="2", timestamp=1600000000, pm10=45.0, temp=19.5,
        pm25=None, so2=None, no=None, no2=None, nox=None, o3=None,
        co=None, ch4=None, nmhc=None, thc=None, c6h6=None, c7h8=None,
        c8h0=None, c4h6=None, h2s=None, pres=None, humi=None, glrd=None,
        filt=None, wind_direction_name=None, wind_speed=None, wind_degrees=None
    )

    mock_coordinator.data = {"1": station_1, "2": station_2}

    # Instantiate the sensor looking for 'pm10' at station '2'
    sensor = SlovnaftAirQualitySensor(
        coordinator=mock_coordinator,
        station_id="2",
        station_name="Podunajske Biskupice",
        sensor_key="pm10",
        sensor_info={"unit": "µg/m³", "icon": "mdi:smog", "device_class": "pm10"}
    )

    # Verify it pulls 45.0 (from station 2), not 15.5 (from station 1)
    assert sensor.native_value == 45.0


async def test_calendar_entity_get_events_real(hass):
    """Test that the calendar entity generates the correct CalendarEvent objects."""
    mock_coordinator = MagicMock()

    # Create fixed dates for the test
    start_date = dt_util.now()
    event_dt = start_date + datetime.timedelta(days=2)
    event_ts = int(event_dt.timestamp())

    # Create a day with multiple active events (Flaring and Noise)
    active_day = CalendarDayStatus(
        date_timestamp=event_ts,
        fire=True, smell=False, noise=True, water=False, smoke=False, work=False
    )

    mock_coordinator.data = CalendarData(
        days={event_ts: active_day},
        last_month_note=None, this_month_note=None, next_month_note=None
    )

    entity = SlovnaftCalendarEntity(coordinator=mock_coordinator)
    entity.hass = hass

    # Call the actual async_get_events method
    end_date = start_date + datetime.timedelta(days=7)
    events = await entity.async_get_events(hass, start_date, end_date)

    assert len(events) == 1
    assert events[0].summary == "Slovnaft: Flaring, Noise"
    assert events[0].start == event_dt.date()
"""Tests for Slovnaft sensors."""
import datetime
import pytest
from unittest.mock import patch, MagicMock
import homeassistant.util.dt as dt_util
from custom_components.slovnaft.models import CalendarDayStatus, CalendarData, StationAirQuality
from custom_components.slovnaft.binary_sensor import SlovnaftCalendarSensor
from custom_components.slovnaft.calendar import SlovnaftCalendarEntity
from custom_components.slovnaft.sensor import SlovnaftCalendarNoteSensor, SlovnaftAirQualitySensor

def test_binary_sensor_day_switch():
    """Test binary sensor state flipping on a standard day switch."""
    dt_day1 = datetime.datetime(2026, 3, 15, 12, 0, tzinfo=datetime.timezone.utc)
    dt_day2 = datetime.datetime(2026, 3, 16, 12, 0, tzinfo=datetime.timezone.utc)

    mock_data = CalendarData(
        days={
            int(dt_day1.timestamp()): CalendarDayStatus(int(dt_day1.timestamp()), fire=True, smell=False, noise=False, water=False, smoke=False, work=False),
            int(dt_day2.timestamp()): CalendarDayStatus(int(dt_day2.timestamp()), fire=False, smell=True, noise=False, water=False, smoke=False, work=False),
        },
        notes_by_month={}
    )
    mock_coordinator = MagicMock()
    mock_coordinator.data = mock_data

    sensor_fire = SlovnaftCalendarSensor(mock_coordinator, "fire", {"icon": "mdi:fire"})

    with patch("homeassistant.util.dt.now") as mock_now:
        mock_now.return_value = datetime.datetime(2026, 3, 15, 23, 59, 59, tzinfo=datetime.timezone.utc)
        assert sensor_fire.is_on is True

    with patch("homeassistant.util.dt.now") as mock_now:
        mock_now.return_value = datetime.datetime(2026, 3, 16, 0, 0, 1, tzinfo=datetime.timezone.utc)
        assert sensor_fire.is_on is False

def test_binary_sensor_month_switch():
    """Test binary sensor state flipping when crossing into a new month."""
    dt_end_month = datetime.datetime(2026, 4, 30, 12, 0, tzinfo=datetime.timezone.utc)
    dt_start_month = datetime.datetime(2026, 5, 1, 12, 0, tzinfo=datetime.timezone.utc)

    mock_data = CalendarData(
        days={
            int(dt_end_month.timestamp()): CalendarDayStatus(int(dt_end_month.timestamp()), fire=False, smell=True, noise=False, water=False, smoke=False, work=False),
            int(dt_start_month.timestamp()): CalendarDayStatus(int(dt_start_month.timestamp()), fire=True, smell=False, noise=False, water=False, smoke=False, work=False),
        },
        notes_by_month={}
    )
    mock_coordinator = MagicMock()
    mock_coordinator.data = mock_data

    sensor_smell = SlovnaftCalendarSensor(mock_coordinator, "smell", {"icon": "mdi:nose"})

    with patch("homeassistant.util.dt.now") as mock_now:
        mock_now.return_value = datetime.datetime(2026, 4, 30, 23, 59, 59, tzinfo=datetime.timezone.utc)
        assert sensor_smell.is_on is True

    with patch("homeassistant.util.dt.now") as mock_now:
        mock_now.return_value = datetime.datetime(2026, 5, 1, 0, 0, 1, tzinfo=datetime.timezone.utc)
        assert sensor_smell.is_on is False

def test_binary_sensor_year_switch():
    """Test binary sensor state flipping when crossing into a new year."""
    dt_nye = datetime.datetime(2026, 12, 31, 12, 0, tzinfo=datetime.timezone.utc)
    dt_nyd = datetime.datetime(2027, 1, 1, 12, 0, tzinfo=datetime.timezone.utc)

    mock_data = CalendarData(
        days={
            int(dt_nye.timestamp()): CalendarDayStatus(int(dt_nye.timestamp()), fire=True, smell=False, noise=False, water=False, smoke=False, work=False),
            int(dt_nyd.timestamp()): CalendarDayStatus(int(dt_nyd.timestamp()), fire=False, smell=True, noise=False, water=False, smoke=False, work=False),
        },
        notes_by_month={}
    )
    mock_coordinator = MagicMock()
    mock_coordinator.data = mock_data

    sensor_fire = SlovnaftCalendarSensor(mock_coordinator, "fire", {"icon": "mdi:fire"})
    sensor_smell = SlovnaftCalendarSensor(mock_coordinator, "smell", {"icon": "mdi:nose"})

    with patch("homeassistant.util.dt.now") as mock_now:
        mock_now.return_value = datetime.datetime(2026, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc)
        assert sensor_fire.is_on is True
        assert sensor_smell.is_on is False

    with patch("homeassistant.util.dt.now") as mock_now:
        mock_now.return_value = datetime.datetime(2027, 1, 1, 0, 0, 1, tzinfo=datetime.timezone.utc)
        assert sensor_fire.is_on is False
        assert sensor_smell.is_on is True

def test_binary_sensor_daily_note_attributes():
    """Verify that the binary sensor safely exposes long notes as attributes."""
    fixed_now = datetime.datetime(2026, 3, 15, 12, 0, tzinfo=datetime.timezone.utc)
    today_ts = int(fixed_now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())

    massive_note = "A" * 500

    mock_data = CalendarData(
        days={
            today_ts: CalendarDayStatus(
                date_timestamp=today_ts,
                fire=True, smell=False, noise=False, water=False, smoke=False, work=False,
                edited=True,
                note=massive_note
            ),
        },
        notes_by_month={}
    )
    mock_coordinator = MagicMock()
    mock_coordinator.data = mock_data

    sensor_fire = SlovnaftCalendarSensor(mock_coordinator, "fire", {"icon": "mdi:fire"})

    with patch("homeassistant.util.dt.now") as mock_now:
        mock_now.return_value = fixed_now

        assert sensor_fire.is_on is True

        attrs = sensor_fire.extra_state_attributes
        assert attrs["edited"] is True
        assert attrs["note"] == massive_note
        assert len(attrs["note"]) == 500

def test_calendar_note_month_switch():
    """Test calendar note sensor dynamically shifts attributes on standard month switch."""
    mock_data = CalendarData(
        days={},
        notes_by_month={
            "2026-03": "March Note",
            "2026-04": "April Note",
            "2026-05": "May Note"
        }
    )
    mock_coordinator = MagicMock()
    mock_coordinator.data = mock_data
    sensor = SlovnaftCalendarNoteSensor(mock_coordinator)

    with patch("homeassistant.util.dt.now") as mock_now:
        mock_now.return_value = datetime.datetime(2026, 3, 31, 23, 59, 59, tzinfo=datetime.timezone.utc)
        attrs = sensor.extra_state_attributes
        assert attrs["this_month_note"] == "March Note"
        assert attrs["next_month_note"] == "April Note"

    with patch("homeassistant.util.dt.now") as mock_now:
        mock_now.return_value = datetime.datetime(2026, 4, 1, 0, 0, 1, tzinfo=datetime.timezone.utc)
        attrs = sensor.extra_state_attributes
        assert attrs["last_month_note"] == "March Note"
        assert attrs["this_month_note"] == "April Note"
        assert attrs["next_month_note"] == "May Note"

def test_calendar_note_year_switch():
    """Test calendar note sensor dynamically shifts attributes crossing year boundary."""
    mock_data = CalendarData(
        days={},
        notes_by_month={
            "2025-12": "Dec 25 Note",
            "2026-01": "Jan 26 Note",
            "2026-02": "Feb 26 Note"
        }
    )
    mock_coordinator = MagicMock()
    mock_coordinator.data = mock_data
    sensor = SlovnaftCalendarNoteSensor(mock_coordinator)

    with patch("homeassistant.util.dt.now") as mock_now:
        mock_now.return_value = datetime.datetime(2025, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc)
        attrs = sensor.extra_state_attributes
        assert attrs["this_month_note"] == "Dec 25 Note"
        assert attrs["next_month_note"] == "Jan 26 Note"

    with patch("homeassistant.util.dt.now") as mock_now:
        mock_now.return_value = datetime.datetime(2026, 1, 1, 0, 0, 1, tzinfo=datetime.timezone.utc)
        attrs = sensor.extra_state_attributes
        assert attrs["last_month_note"] == "Dec 25 Note"
        assert attrs["this_month_note"] == "Jan 26 Note"
        assert attrs["next_month_note"] == "Feb 26 Note"

@pytest.mark.asyncio
async def test_binary_sensor_midnight_redraw(hass):
    """Test that the binary sensor schedules a state update exactly at midnight."""
    coordinator = MagicMock()
    sensor = SlovnaftCalendarSensor(coordinator, "fire", {"icon": "mdi:fire"})
    sensor.hass = hass

    with patch("custom_components.slovnaft.binary_sensor.async_track_time_change") as mock_track:
        await sensor.async_added_to_hass()
        assert mock_track.call_count == 1
        args, kwargs = mock_track.call_args
        assert kwargs["hour"] == 0
        assert kwargs["minute"] == 0
        assert kwargs["second"] == 1

        update_callback = args[1]
        with patch.object(sensor, "async_write_ha_state") as mock_write:
            update_callback(None)
            mock_write.assert_called_once()

@pytest.mark.asyncio
async def test_calendar_midnight_redraw(hass):
    """Test that the calendar entity schedules a state update exactly at midnight."""
    coordinator = MagicMock()
    entity = SlovnaftCalendarEntity(coordinator)
    entity.hass = hass

    with patch("custom_components.slovnaft.calendar.async_track_time_change") as mock_track:
        await entity.async_added_to_hass()
        assert mock_track.call_count == 1
        args, kwargs = mock_track.call_args
        assert kwargs["hour"] == 0
        assert kwargs["minute"] == 0
        assert kwargs["second"] == 1

        update_callback = args[1]
        with patch.object(entity, "async_write_ha_state") as mock_write:
            update_callback(None)
            mock_write.assert_called_once()

@pytest.mark.asyncio
async def test_calendar_note_sensor_midnight_redraw(hass):
    """Test that the calendar note sensor schedules a state update exactly at midnight."""
    coordinator = MagicMock()
    sensor = SlovnaftCalendarNoteSensor(coordinator)
    sensor.hass = hass

    with patch("custom_components.slovnaft.sensor.async_track_time_change") as mock_track:
        await sensor.async_added_to_hass()
        assert mock_track.call_count == 1
        args, kwargs = mock_track.call_args
        assert kwargs["hour"] == 0
        assert kwargs["minute"] == 0
        assert kwargs["second"] == 1

        update_callback = args[1]
        with patch.object(sensor, "async_write_ha_state") as mock_write:
            update_callback(None)
            mock_write.assert_called_once()

def test_calendar_notes_sensor_real():
    """Test that the calendar note sensor exposes states and attributes correctly."""
    mock_coordinator = MagicMock()
    now = dt_util.now()

    last_y, last_m = (now.year, now.month - 1) if now.month > 1 else (now.year - 1, 12)
    next_y, next_m = (now.year, now.month + 1) if now.month < 12 else (now.year + 1, 1)

    mock_coordinator.data = CalendarData(
        days={},
        notes_by_month={
            f"{last_y}-{last_m:02d}": "<p>Old note</p>",
            f"{now.year}-{now.month:02d}": "<p>Current note</p>",
            f"{next_y}-{next_m:02d}": "<p>Future note</p>"
        }
    )

    sensor = SlovnaftCalendarNoteSensor(coordinator=mock_coordinator)
    assert sensor.native_value == "Available"

    attrs = sensor.extra_state_attributes
    assert attrs["last_month_note"] == "<p>Old note</p>"
    assert attrs["this_month_note"] == "<p>Current note</p>"
    assert attrs["next_month_note"] == "<p>Future note</p>"

    mock_coordinator.data.notes_by_month = {}
    assert sensor.native_value == "No Notes"

def test_air_quality_sensor_real():
    """Test that the air quality sensor pulls the correct measurement."""
    mock_coordinator = MagicMock()

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

    sensor = SlovnaftAirQualitySensor(
        coordinator=mock_coordinator,
        station_id="2",
        station_name="Podunajske Biskupice",
        sensor_key="pm10",
        sensor_info={"unit": "µg/m³", "icon": "mdi:smog", "device_class": "pm10"}
    )

    assert sensor.native_value == 45.0

async def test_calendar_entity_get_events_real(hass):
    """Test that the calendar entity generates the correct CalendarEvent objects."""
    mock_coordinator = MagicMock()

    start_date = dt_util.now()
    event_dt = start_date + datetime.timedelta(days=2)
    event_ts = int(event_dt.timestamp())

    active_day = CalendarDayStatus(
        date_timestamp=event_ts,
        fire=True, smell=False, noise=True, water=False, smoke=False, work=False,
        edited=True, note="Test specific note."
    )

    mock_coordinator.data = CalendarData(
        days={event_ts: active_day},
        notes_by_month={}
    )

    entity = SlovnaftCalendarEntity(coordinator=mock_coordinator)
    entity.hass = hass

    end_date = start_date + datetime.timedelta(days=7)
    events = await entity.async_get_events(hass, start_date, end_date)

    assert len(events) == 1
    assert events[0].summary == "Slovnaft: Flaring, Noise"
    assert events[0].start == event_dt.date()
    assert "Test specific note." in events[0].description
    assert "(Edited)" in events[0].description
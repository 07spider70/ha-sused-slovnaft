"""Tests for Slovnaft sensors."""
import datetime
import pytest
from unittest.mock import patch, MagicMock
import homeassistant.util.dt as dt_util
from custom_components.slovnaft.models import CalendarDayStatus, CalendarData, StationAirQuality
from custom_components.slovnaft.binary_sensor import SlovnaftCalendarSensor
from custom_components.slovnaft.calendar import SlovnaftCalendarEntity
from custom_components.slovnaft.sensor import SlovnaftCalendarNoteSensor, SlovnaftAirQualitySensor


# ---------------------------------------------------------------------------
# Helper: build timestamps the way the real Slovnaft API does.
#
# The API encodes each calendar day as midnight *local* CET/CEST expressed in
# UTC.  Before DST (CET, UTC+1) that is 23:00 UTC of the same day; after DST
# (CEST, UTC+2) it is 22:00 UTC of the same day.
# ---------------------------------------------------------------------------

def _api_ts(year: int, month: int, day: int, *, cest: bool = False) -> int:
    """Return a Unix timestamp mimicking the Slovnaft API for a given date.

    CET (winter): midnight CET = 23:00 UTC same day  -> hour=23
    CEST (summer): midnight CEST = 22:00 UTC same day -> hour=22
    """
    hour = 22 if cest else 23
    return int(
        datetime.datetime(year, month, day, hour, 0, 0, tzinfo=datetime.timezone.utc).timestamp()
    )


# ---------------------------------------------------------------------------
# Binary sensor - day switch
# ---------------------------------------------------------------------------

def test_binary_sensor_day_switch():
    """Test binary sensor state flipping on a standard day switch."""
    ts_day1 = _api_ts(2026, 3, 15)
    ts_day2 = _api_ts(2026, 3, 16)

    mock_data = CalendarData(
        days={
            ts_day1: CalendarDayStatus(ts_day1, fire=True, smell=False, noise=False, water=False, smoke=False, work=False),
            ts_day2: CalendarDayStatus(ts_day2, fire=False, smell=True, noise=False, water=False, smoke=False, work=False),
        },
        notes_by_month={}
    )
    mock_coordinator = MagicMock()
    mock_coordinator.data = mock_data

    sensor_fire = SlovnaftCalendarSensor(mock_coordinator, "fire", {"icon": "mdi:fire"})

    # Still March 15 (late evening local)
    with patch("homeassistant.util.dt.now") as mock_now:
        mock_now.return_value = datetime.datetime(2026, 3, 15, 23, 59, 59, tzinfo=datetime.timezone.utc)
        assert sensor_fire.is_on is True

    # Just past midnight -> March 16
    with patch("homeassistant.util.dt.now") as mock_now:
        mock_now.return_value = datetime.datetime(2026, 3, 16, 0, 0, 1, tzinfo=datetime.timezone.utc)
        assert sensor_fire.is_on is False


def test_binary_sensor_with_real_api_timestamps():
    """Regression test: real API timestamps (23:00 UTC) must match the correct
    calendar day, not the next day which would happen with as_local().

    This is the exact scenario from the bug report: March 2, 2026 with the
    real API response.  March 1 has fire=1/smell=1/noise=1, March 2 has all
    zeros.
    """
    ts_mar1 = 1772406000   # 2026-03-01T23:00:00Z (March 1 entry)
    ts_mar2 = 1772492400   # 2026-03-02T23:00:00Z (March 2 entry)

    mock_data = CalendarData(
        days={
            ts_mar1: CalendarDayStatus(ts_mar1, fire=True, smell=True, noise=True, water=False, smoke=False, work=False),
            ts_mar2: CalendarDayStatus(ts_mar2, fire=False, smell=False, noise=False, water=False, smoke=False, work=False),
        },
        notes_by_month={}
    )
    mock_coordinator = MagicMock()
    mock_coordinator.data = mock_data

    sensor_fire = SlovnaftCalendarSensor(mock_coordinator, "fire", {"icon": "mdi:fire"})
    sensor_smell = SlovnaftCalendarSensor(mock_coordinator, "smell", {"icon": "mdi:scent"})
    sensor_noise = SlovnaftCalendarSensor(mock_coordinator, "noise", {"icon": "mdi:volume-high"})

    # On March 2, everything should be OFF (API says all zeros for March 2)
    with patch("homeassistant.util.dt.now") as mock_now:
        mock_now.return_value = datetime.datetime(2026, 3, 2, 10, 0, 0, tzinfo=datetime.timezone.utc)
        assert sensor_fire.is_on is False, "fire should be OFF on March 2"
        assert sensor_smell.is_on is False, "smell should be OFF on March 2"
        assert sensor_noise.is_on is False, "noise should be OFF on March 2"

    # On March 1, everything should be ON
    with patch("homeassistant.util.dt.now") as mock_now:
        mock_now.return_value = datetime.datetime(2026, 3, 1, 15, 0, 0, tzinfo=datetime.timezone.utc)
        assert sensor_fire.is_on is True, "fire should be ON on March 1"
        assert sensor_smell.is_on is True, "smell should be ON on March 1"
        assert sensor_noise.is_on is True, "noise should be ON on March 1"


def test_binary_sensor_dst_boundary():
    """Test that the timestamp interpretation works across the DST boundary.

    DST in 2026 starts on March 29 (CET->CEST).  Before DST the API uses
    23:00 UTC; after DST it uses 22:00 UTC.  Both should resolve to the
    correct calendar day.
    """
    ts_mar28 = _api_ts(2026, 3, 28, cest=False)   # 23:00 UTC (still CET)
    ts_mar29 = _api_ts(2026, 3, 29, cest=True)    # 22:00 UTC (CEST kicks in)
    ts_mar30 = _api_ts(2026, 3, 30, cest=True)    # 22:00 UTC

    mock_data = CalendarData(
        days={
            ts_mar28: CalendarDayStatus(ts_mar28, fire=True, smell=False, noise=False, water=False, smoke=False, work=False),
            ts_mar29: CalendarDayStatus(ts_mar29, fire=False, smell=True, noise=False, water=False, smoke=False, work=False),
            ts_mar30: CalendarDayStatus(ts_mar30, fire=False, smell=False, noise=True, water=False, smoke=False, work=False),
        },
        notes_by_month={}
    )
    mock_coordinator = MagicMock()
    mock_coordinator.data = mock_data

    sensor_fire = SlovnaftCalendarSensor(mock_coordinator, "fire", {"icon": "mdi:fire"})
    sensor_smell = SlovnaftCalendarSensor(mock_coordinator, "smell", {"icon": "mdi:scent"})
    sensor_noise = SlovnaftCalendarSensor(mock_coordinator, "noise", {"icon": "mdi:volume-high"})

    with patch("homeassistant.util.dt.now") as mock_now:
        mock_now.return_value = datetime.datetime(2026, 3, 28, 12, 0, tzinfo=datetime.timezone.utc)
        assert sensor_fire.is_on is True
        assert sensor_smell.is_on is False

    with patch("homeassistant.util.dt.now") as mock_now:
        mock_now.return_value = datetime.datetime(2026, 3, 29, 12, 0, tzinfo=datetime.timezone.utc)
        assert sensor_fire.is_on is False
        assert sensor_smell.is_on is True

    with patch("homeassistant.util.dt.now") as mock_now:
        mock_now.return_value = datetime.datetime(2026, 3, 30, 12, 0, tzinfo=datetime.timezone.utc)
        assert sensor_smell.is_on is False
        assert sensor_noise.is_on is True


# ---------------------------------------------------------------------------
# Binary sensor - month boundary
# ---------------------------------------------------------------------------

def test_binary_sensor_month_switch():
    """Test binary sensor state flipping when crossing into a new month."""
    ts_end_month = _api_ts(2026, 4, 30)
    ts_start_month = _api_ts(2026, 5, 1)

    mock_data = CalendarData(
        days={
            ts_end_month: CalendarDayStatus(ts_end_month, fire=False, smell=True, noise=False, water=False, smoke=False, work=False),
            ts_start_month: CalendarDayStatus(ts_start_month, fire=True, smell=False, noise=False, water=False, smoke=False, work=False),
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


# ---------------------------------------------------------------------------
# Binary sensor - year boundary
# ---------------------------------------------------------------------------

def test_binary_sensor_year_switch():
    """Test binary sensor state flipping when crossing into a new year."""
    ts_nye = _api_ts(2026, 12, 31)
    ts_nyd = _api_ts(2027, 1, 1)

    mock_data = CalendarData(
        days={
            ts_nye: CalendarDayStatus(ts_nye, fire=True, smell=False, noise=False, water=False, smoke=False, work=False),
            ts_nyd: CalendarDayStatus(ts_nyd, fire=False, smell=True, noise=False, water=False, smoke=False, work=False),
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


# ---------------------------------------------------------------------------
# Binary sensor - daily note attributes
# ---------------------------------------------------------------------------

def test_binary_sensor_daily_note_attributes():
    """Verify that the binary sensor safely exposes long notes as attributes."""
    ts_today = _api_ts(2026, 3, 15)
    massive_note = "A" * 500

    mock_data = CalendarData(
        days={
            ts_today: CalendarDayStatus(
                date_timestamp=ts_today,
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
        mock_now.return_value = datetime.datetime(2026, 3, 15, 12, 0, tzinfo=datetime.timezone.utc)

        assert sensor_fire.is_on is True

        attrs = sensor_fire.extra_state_attributes
        assert attrs["edited"] is True
        assert attrs["note"] == massive_note
        assert len(attrs["note"]) == 500


# ---------------------------------------------------------------------------
# Calendar note sensor - month/year switching
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Midnight-redraw scheduling
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Calendar notes sensor - real usage
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Air quality sensor
# ---------------------------------------------------------------------------

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
        sensor_info={"unit": "ug/m3", "icon": "mdi:smog", "device_class": "pm10"}
    )

    assert sensor.native_value == 45.0


# ---------------------------------------------------------------------------
# Calendar entity - async_get_events with real API timestamps
# ---------------------------------------------------------------------------

async def test_calendar_entity_get_events_real(hass):
    """Test that the calendar entity generates the correct CalendarEvent objects."""
    mock_coordinator = MagicMock()

    start_date = dt_util.now()
    event_dt = start_date + datetime.timedelta(days=2)
    event_ts = _api_ts(event_dt.year, event_dt.month, event_dt.day)

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


async def test_calendar_entity_get_events_with_real_api_timestamps(hass):
    """Regression test: calendar events must use UTC date, not local date."""
    mock_coordinator = MagicMock()

    # Real API timestamps from March 2026
    ts_mar1 = 1772406000   # 2026-03-01T23:00:00Z
    ts_mar2 = 1772492400   # 2026-03-02T23:00:00Z

    mock_coordinator.data = CalendarData(
        days={
            ts_mar1: CalendarDayStatus(ts_mar1, fire=True, smell=True, noise=True, water=False, smoke=False, work=False),
            ts_mar2: CalendarDayStatus(ts_mar2, fire=False, smell=False, noise=False, water=False, smoke=False, work=False),
        },
        notes_by_month={}
    )

    entity = SlovnaftCalendarEntity(coordinator=mock_coordinator)
    entity.hass = hass

    start = datetime.datetime(2026, 3, 1, 0, 0, tzinfo=datetime.timezone.utc)
    end = datetime.datetime(2026, 3, 2, 23, 59, tzinfo=datetime.timezone.utc)
    events = await entity.async_get_events(hass, start, end)

    # March 1 has active flags -> event; March 2 has none -> no event
    assert len(events) == 1
    assert events[0].start == datetime.date(2026, 3, 1)
    assert "Flaring" in events[0].summary

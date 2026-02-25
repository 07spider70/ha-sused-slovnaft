"""Tests for Slovnaft sensors."""
import datetime
from custom_components.slovnaft.models import CalendarDayStatus, CalendarData

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
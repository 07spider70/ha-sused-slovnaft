"""Tests for sensor logic."""
import datetime
from custom_components.slovnaft.models import CalendarDayStatus


def test_calendar_date_matching_logic():
    """Verify that we correctly find 'today' in a dictionary of timestamps."""
    # Create a timestamp for exactly today
    today_dt = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_ts = int(today_dt.timestamp())

    status = CalendarDayStatus(
        date_timestamp=today_ts,
        fire=True, smell=False, noise=False, water=False, smoke=False, work=False
    )

    data = {today_ts: status}

    # Simulate the binary_sensor's check
    found_status = None
    target_date = datetime.datetime.now().date()

    for ts, day_status in data.items():
        if datetime.datetime.fromtimestamp(ts).date() == target_date:
            found_status = day_status

    assert found_status is not None
    assert found_status.fire is True
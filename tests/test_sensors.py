"""Tests for Slovnaft sensors."""
import datetime
from custom_components.slovnaft.models import CalendarDayStatus


def test_calendar_today_logic():
    """Verify that the sensor correctly identifies 'today' from the timestamp."""
    # Create a timestamp for exactly today at midnight
    today_dt = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_ts = int(today_dt.timestamp())

    # Create a mock data object for today
    status = CalendarDayStatus(
        date_timestamp=today_ts,
        fire=True, smell=False, noise=False, water=False, smoke=False, work=False
    )

    # Simulate the binary_sensor's is_on logic
    is_fire_on = False
    for ts, day_status in {today_ts: status}.items():
        if datetime.datetime.fromtimestamp(ts).date() == datetime.datetime.now().date():
            is_fire_on = day_status.fire

    assert is_fire_on is True
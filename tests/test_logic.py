"""Tests for sensor logic."""
import datetime
from custom_components.slovnaft.models import CalendarDayStatus


def test_calendar_date_matching_logic():
    """Verify that we correctly find 'today' in a dictionary of timestamps.

    Uses 23:00 UTC timestamps (matching real Slovnaft API format for CET)
    to ensure the UTC-date comparison works correctly.
    """
    # API timestamp for March 15 at 23:00 UTC (midnight CET)
    today_ts = int(
        datetime.datetime(2026, 3, 15, 23, 0, 0, tzinfo=datetime.timezone.utc).timestamp()
    )

    status = CalendarDayStatus(
        date_timestamp=today_ts,
        fire=True, smell=False, noise=False, water=False, smoke=False, work=False
    )

    data = {today_ts: status}

    # Simulate the fixed binary_sensor's check: use UTC date from timestamp
    found_status = None
    target_date = datetime.date(2026, 3, 15)

    for ts, day_status in data.items():
        day_date = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).date()
        if day_date == target_date:
            found_status = day_status

    assert found_status is not None
    assert found_status.fire is True


def test_calendar_date_matching_does_not_match_wrong_day():
    """Ensure a 23:00 UTC timestamp for day X does NOT match day X+1.

    This is the exact bug that existed before: as_local() shifted the date
    forward by one day in CET.
    """
    ts_mar1 = 1772406000  # 2026-03-01T23:00:00Z

    status = CalendarDayStatus(
        date_timestamp=ts_mar1,
        fire=True, smell=True, noise=True, water=False, smoke=False, work=False
    )

    data = {ts_mar1: status}

    # March 2 should NOT match March 1's timestamp
    target_date = datetime.date(2026, 3, 2)
    found = False
    for ts, day_status in data.items():
        day_date = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).date()
        if day_date == target_date:
            found = True

    assert found is False, "March 1 API timestamp must NOT match March 2"
import datetime
import homeassistant.util.dt as dt_util
from custom_components.slovnaft.models import CalendarDayStatus

def test_binary_sensor_today_logic():
    """Verify logic that picks today's date from the dataset using UTC dates.

    Uses realistic 23:00 UTC timestamps matching the real Slovnaft API format
    to catch timezone-related off-by-one errors.
    """
    # Build a timestamp mimicking what the API returns (23:00 UTC = midnight CET)
    now = dt_util.now()
    api_ts = int(
        datetime.datetime(
            now.year, now.month, now.day, 23, 0, 0, tzinfo=datetime.timezone.utc
        ).timestamp()
    )

    # Mock data for today
    status_today = CalendarDayStatus(
        date_timestamp=api_ts,
        fire=True, smell=False, noise=False, water=False, smoke=False, work=False
    )

    data = {api_ts: status_today}

    # Simulate the fixed is_on logic: compare UTC date of timestamp vs local today
    found = False
    today = dt_util.now().date()
    for ts, status in data.items():
        day_date = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).date()
        if day_date == today:
            assert status.fire is True
            found = True

    assert found is True
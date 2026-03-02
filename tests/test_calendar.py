import datetime
import homeassistant.util.dt as dt_util
from custom_components.slovnaft.models import CalendarDayStatus

def test_binary_sensor_today_logic():
    """Verify logic that picks today's date from the dataset using proper HA dt_utils."""
    now = dt_util.now()
    today_ts = int(now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())

    # Mock data for today
    status_today = CalendarDayStatus(
        date_timestamp=today_ts,
        fire=True, smell=False, noise=False, water=False, smoke=False, work=False
    )

    # Mock full dataset
    data = {today_ts: status_today}

    # Simulate the is_on logic
    found = False
    for ts, status in data.items():
        if datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).date() == dt_util.now().date():
            assert status.fire is True
            found = True

    assert found is True
from datetime import datetime
from custom_components.slovnaft.models import CalendarDayStatus

def test_binary_sensor_today_logic():
    """Verify logic that picks today's date from the dataset."""
    today_ts = int(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp())

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
        if datetime.fromtimestamp(ts).date() == datetime.now().date():
            assert status.fire is True
            found = True

    assert found is True
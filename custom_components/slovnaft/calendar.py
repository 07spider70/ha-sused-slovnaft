"""Calendar platform for the Sused Slovnaft integration."""
import datetime
from typing import Any

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.event import async_track_time_change
import homeassistant.util.dt as dt_util

from . import SlovnaftConfigEntry
from .const import DOMAIN
from .models import CalendarDayStatus

PARALLEL_UPDATES = 0

async def async_setup_entry(hass: HomeAssistant, entry: SlovnaftConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    if not entry.runtime_data.calendar_coordinator:
        return
    coordinator = entry.runtime_data.calendar_coordinator
    async_add_entities([SlovnaftCalendarEntity(coordinator)])


class SlovnaftCalendarEntity(CoordinatorEntity, CalendarEntity):
    """A calendar entity displaying Slovnaft planned events."""
    _attr_has_entity_name = True
    _attr_icon = "mdi:calendar-alert"

    def __init__(self, coordinator: Any) -> None:
        """Initialize the calendar entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_calendar_view"
        self.translation_key = "calendar_view"

    async def async_added_to_hass(self) -> None:
        """Run when entity is added to Home Assistant."""
        await super().async_added_to_hass()

        @callback
        def _update_state(_now):
            """Force a UI redraw without hitting the API."""
            self.async_write_ha_state()

        # Schedule the UI to redraw exactly at 00:00:01 every single day
        self.async_on_remove(
            async_track_time_change(
                self.hass, _update_state, hour=0, minute=0, second=1
            )
        )

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, "calendar")},
            name="Slovnaft Calendar Events",
            manufacturer="Slovnaft",
        )

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming calendar event."""
        if not self.coordinator.data or not self.coordinator.data.days:
            return None

        # Use Home Assistant's timezone-aware util
        today = dt_util.now().date()
        calendar_days = self.coordinator.data.days

        for timestamp in sorted(calendar_days.keys()):
            # Use local time for the timestamp based on HA config
            dt = dt_util.as_local(datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)).date()
            if dt >= today:
                status = calendar_days[timestamp]
                event = self._generate_ha_event(dt, status)
                if event:
                    return event
        return None

    async def async_get_events(self, hass: HomeAssistant, start_date: datetime.datetime, end_date: datetime.datetime) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        if not self.coordinator.data or not self.coordinator.data.days:
            return []

        events = []
        for timestamp, status in self.coordinator.data.days.items():
            dt = dt_util.as_local(datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)).date()
            if start_date.date() <= dt <= end_date.date():
                event = self._generate_ha_event(dt, status)
                if event:
                    events.append(event)
        return events

    @staticmethod
    def _generate_ha_event(event_date: datetime.date, status: CalendarDayStatus) -> CalendarEvent | None:
        """Helper to convert a DayStatus into a Home Assistant CalendarEvent."""
        active_flags = []
        if status.fire:
            active_flags.append("Flaring")
        if status.smell:
            active_flags.append("Odor")
        if status.noise:
            active_flags.append("Noise")
        if status.smoke:
            active_flags.append("Smoke")
        if status.water:
            active_flags.append("Water Activity")
        if status.work:
            active_flags.append("Maintenance")

        if not active_flags:
            return None

        summary = f"Slovnaft: {', '.join(active_flags)}"
        end_date = event_date + datetime.timedelta(days=1)

        return CalendarEvent(
            start=event_date,
            end=end_date,
            summary=summary,
            description="Official transparent refinery status.",
        )
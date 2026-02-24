"""Calendar platform for the Sused Slovnaft integration."""
import datetime
from typing import Any, Dict
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

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
        self.translation_key = "calendar_view"  # THE TRANSLATION MAGIC KEY

    @property
    def device_info(self) -> Dict[str, Any]:
        return {
            "identifiers": {(DOMAIN, "calendar")},
            "name": "Slovnaft Calendar Events",
            "manufacturer": "Slovnaft",
        }

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming calendar event."""
        if not self.coordinator.data:
            return None

        today = datetime.datetime.now().date()
        for timestamp in sorted(self.coordinator.data.keys()):
            dt = datetime.datetime.fromtimestamp(timestamp).date()
            if dt >= today:
                status = self.coordinator.data[timestamp]
                event = self._generate_ha_event(dt, status)
                if event:
                    return event
        return None

    async def async_get_events(self, hass: HomeAssistant, start_date: datetime.datetime, end_date: datetime.datetime) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        if not self.coordinator.data:
            return []

        events = []
        for timestamp, status in self.coordinator.data.items():
            dt = datetime.datetime.fromtimestamp(timestamp).date()
            if start_date.date() <= dt <= end_date.date():
                event = self._generate_ha_event(dt, status)
                if event:
                    events.append(event)
        return events

    def _generate_ha_event(self, event_date: datetime.date, status: CalendarDayStatus) -> CalendarEvent | None:
        """Helper to convert a DayStatus into a Home Assistant CalendarEvent."""
        active_flags = []
        if status.fire: active_flags.append("Flaring")
        if status.smell: active_flags.append("Odor")
        if status.noise: active_flags.append("Noise")
        if status.smoke: active_flags.append("Smoke")
        if status.water: active_flags.append("Water Activity")
        if status.work: active_flags.append("Maintenance")

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
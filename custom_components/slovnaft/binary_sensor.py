"""Binary sensor platform for the Sused Slovnaft Calendar."""
import datetime
import logging
from typing import Any, Dict

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import homeassistant.util.dt as dt_util

from . import SlovnaftConfigEntry
from .models import CalendarDayStatus
from .const import DOMAIN, BINARY_SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 0

async def async_setup_entry(hass: HomeAssistant, entry: SlovnaftConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    if not entry.runtime_data.calendar_coordinator:
        return

    coordinator = entry.runtime_data.calendar_coordinator
    entities = []
    for sensor_key, sensor_info in BINARY_SENSOR_TYPES.items():
        entities.append(SlovnaftCalendarSensor(coordinator, sensor_key, sensor_info))

    async_add_entities(entities)


class SlovnaftCalendarSensor(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: Any, sensor_key: str, sensor_info: Dict[str, Any]) -> None:
        super().__init__(coordinator)
        self.sensor_key = sensor_key
        self._attr_unique_id = f"{DOMAIN}_calendar_{sensor_key}"
        self.translation_key = sensor_key
        self._attr_icon = sensor_info.get("icon")

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

    def _get_today_status(self) -> CalendarDayStatus | None:
        """Helper method to get today's CalendarDayStatus.

        The API timestamps represent midnight local time (CET/CEST) stored as
        UTC, so the *UTC date* of each timestamp equals the intended calendar
        day.  We therefore compare UTC dates from the API against the user's
        local date to find today's entry.
        """
        if not self.coordinator.data or not self.coordinator.data.days:
            _LOGGER.debug("No calendar data available for binary sensor %s", self.sensor_key)
            return None

        today = dt_util.now().date()
        _LOGGER.debug(
            "Looking up calendar status for sensor '%s' on local date %s (available days: %d)",
            self.sensor_key,
            today,
            len(self.coordinator.data.days),
        )

        for timestamp, day_status in self.coordinator.data.days.items():
            # Use UTC date — the API encodes each calendar day at 23:00/22:00
            # UTC (midnight CET/CEST), so the UTC date is the correct day.
            day_date = datetime.datetime.fromtimestamp(
                timestamp, tz=datetime.timezone.utc
            ).date()
            if day_date == today:
                _LOGGER.debug(
                    "Matched today (%s) to API timestamp %s (UTC %s) for sensor '%s': %s=%s",
                    today,
                    timestamp,
                    day_date,
                    self.sensor_key,
                    self.sensor_key,
                    getattr(day_status, self.sensor_key, None),
                )
                return day_status

        _LOGGER.debug(
            "No matching calendar entry found for today (%s) in %d available days for sensor '%s'",
            today,
            len(self.coordinator.data.days),
            self.sensor_key,
        )
        return None

    @property
    def is_on(self) -> bool:
        today_status = self._get_today_status()
        if today_status:
            return getattr(today_status, self.sensor_key, False)
        return False

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Expose unlimited length day notes and edited flags as attributes"""
        today_status = self._get_today_status()
        if today_status:
            return {
                "edited": today_status.edited,
                "note": today_status.note,
            }
        return {}
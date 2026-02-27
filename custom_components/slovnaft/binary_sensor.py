"""Binary sensor platform for the Sused Slovnaft Calendar."""
import datetime
from typing import Any, Dict

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import homeassistant.util.dt as dt_util

from . import SlovnaftConfigEntry
from .const import DOMAIN, BINARY_SENSOR_TYPES

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

    @property
    def is_on(self) -> bool:
        if not self.coordinator.data or not self.coordinator.data.days:
            return False

        today = dt_util.now().date()
        for timestamp, day_status in self.coordinator.data.days.items():
            dt = dt_util.as_local(datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)).date()
            if dt == today:
                return getattr(day_status, self.sensor_key, False)
        return False
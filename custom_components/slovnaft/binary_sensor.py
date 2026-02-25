"""Binary sensor platform for the Sused Slovnaft Calendar."""
import datetime
from typing import Any, Dict
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

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
        self._attr_icon = sensor_info["icon"]

    @property
    def device_info(self) -> Dict[str, Any]:
        return {
            "identifiers": {(DOMAIN, "calendar")},
            "name": "Slovnaft Calendar Events",
            "manufacturer": "Slovnaft",
        }

    @property
    def is_on(self) -> bool:
        if not self.coordinator.data or not self.coordinator.data.days:
            return False

        today = datetime.datetime.now().date()
        for timestamp, day_status in self.coordinator.data.days.items():
            if datetime.datetime.fromtimestamp(timestamp).date() == today:
                return getattr(day_status, self.sensor_key, False)
        return False
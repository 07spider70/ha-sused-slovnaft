"""Sensor platform for the Sused Slovnaft integration."""
from typing import Any, Dict, Optional
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.event import async_track_time_change

from . import SlovnaftConfigEntry
from .const import DOMAIN, STATIONS, SENSOR_TYPES
from .models import StationAirQuality

PARALLEL_UPDATES = 0

async def async_setup_entry(hass: HomeAssistant, entry: SlovnaftConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    entities = []

    if entry.runtime_data.env_coordinator:
        coordinator = entry.runtime_data.env_coordinator
        user_stations = entry.data.get("stations", [])

        for station_id, station_name in STATIONS.items():
            if station_id in user_stations:
                for sensor_key, sensor_info in SENSOR_TYPES.items():
                    entities.append(SlovnaftAirQualitySensor(coordinator, station_id, station_name, sensor_key, sensor_info))

    if entry.runtime_data.calendar_coordinator:
        entities.append(SlovnaftCalendarNoteSensor(entry.runtime_data.calendar_coordinator))

    if entities:
        async_add_entities(entities)


class SlovnaftAirQualitySensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: Any, station_id: str, station_name: str, sensor_key: str, sensor_info: Dict[str, Any]) -> None:
        super().__init__(coordinator)
        self.station_id = station_id
        self.station_name = station_name
        self.sensor_key = sensor_key

        self._attr_unique_id = f"{DOMAIN}_{station_id}_{sensor_key}"
        self.translation_key = sensor_key

        self._attr_native_unit_of_measurement = sensor_info.get("unit")
        self._attr_icon = sensor_info.get("icon")
        self._attr_device_class = sensor_info.get("device_class")
        self._attr_state_class = SensorStateClass.MEASUREMENT if self._attr_native_unit_of_measurement else None

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.station_id)},
            name=f"Slovnaft Station - {self.station_name}",
            manufacturer="Slovnaft",
        )

    @property
    def native_value(self) -> Optional[Any]:
        stations_data: Dict[str, StationAirQuality] = self.coordinator.data
        if not stations_data:
            return None
        station = stations_data.get(self.station_id)
        if station:
            return getattr(station, self.sensor_key, None)
        return None


class SlovnaftCalendarNoteSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_icon = "mdi:note-text"

    def __init__(self, coordinator: Any) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_calendar_notes"
        self.translation_key = "calendar_notes"

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
    def native_value(self) -> str | None:
        """The main state must be under 255 chars."""
        if not self.coordinator.data:
            return None
        return "Available" if self.coordinator.data.this_month_note else "No Notes"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Expose the massive text blocks as attributes!"""
        if not self.coordinator.data:
            return {}
        return {
            "last_month_note": self.coordinator.data.last_month_note,
            "this_month_note": self.coordinator.data.this_month_note,
            "next_month_note": self.coordinator.data.next_month_note,
        }
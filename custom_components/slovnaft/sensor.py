"""Sensor platform for the Sused Slovnaft integration."""
from typing import Any, Dict, Optional
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SlovnaftConfigEntry
from .const import DOMAIN, STATIONS, SENSOR_TYPES
from .models import StationAirQuality

PARALLEL_UPDATES = 0

async def async_setup_entry(hass: HomeAssistant, entry: SlovnaftConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    if not entry.runtime_data.env_coordinator:
        return

    coordinator = entry.runtime_data.env_coordinator
    user_stations = entry.data.get("stations", [])
    entities = []

    for station_id, station_name in STATIONS.items():
        if station_id in user_stations:
            for sensor_key, sensor_info in SENSOR_TYPES.items():
                entities.append(SlovnaftAirQualitySensor(coordinator, station_id, station_name, sensor_key, sensor_info))

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
        self._attr_native_unit_of_measurement = sensor_info["unit"]
        self._attr_icon = sensor_info["icon"]
        self._attr_device_class = sensor_info["device_class"]
        self._attr_state_class = SensorStateClass.MEASUREMENT if sensor_info["unit"] else None

    @property
    def device_info(self) -> Dict[str, Any]:
        return {
            "identifiers": {(DOMAIN, self.station_id)},
            "name": f"Slovnaft Station - {self.station_name}",
            "manufacturer": "Slovnaft",
        }

    @property
    def native_value(self) -> Optional[Any]:
        stations_data: Dict[str, StationAirQuality] = self.coordinator.data
        if not stations_data: return None
        station = stations_data.get(self.station_id)
        if station: return getattr(station, self.sensor_key, None)
        return None
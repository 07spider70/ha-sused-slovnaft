"""Constants for the Sused Slovnaft integration."""
from homeassistant.components.sensor import SensorDeviceClass

DOMAIN = "slovnaft"

# API Endpoints
BASE_URL = "https://sused.slovnaft.sk/api"
ENV_ENDPOINT = f"{BASE_URL}/environment"
CALENDAR_ENDPOINT = f"{BASE_URL}/calendar"

# Station Mappings
STATIONS = {
    "116": "Rovinka",
    "117": "Podunajské Biskupice",
    "118": "Vlčie hrdlo"
}

# Update Intervals (in minutes)
ENV_ENDPOINT_DEFAULT_INTERVAL_MIN = 15 # 15 minutes
ENV_ENDPOINT_MIN_INTERVAL_MIN = 15      # 15 minutes
ENV_ENDPOINT_MAX_INTERVAL_MIN = 24*60  # 24 hours
CALENDAR_ENDPOINT_DEFAULT_INTERVAL_HOURS = 12  # 12 hours

# Air Quality Sensor Definitions
SENSOR_TYPES = {
    "pm10": {"unit": "µg/m³", "icon": "mdi:blur", "device_class": SensorDeviceClass.PM10},
    "pm25": {"unit": "µg/m³", "icon": "mdi:blur", "device_class": SensorDeviceClass.PM25},
    "so2": {"unit": "µg/m³", "icon": "mdi:molecule-co2", "device_class": SensorDeviceClass.SULPHUR_DIOXIDE},
    "no": {"unit": "µg/m³", "icon": "mdi:molecule", "device_class": SensorDeviceClass.NITROGEN_MONOXIDE},
    "no2": {"unit": "µg/m³", "icon": "mdi:smog", "device_class": SensorDeviceClass.NITROGEN_DIOXIDE},
    "nox": {"unit": "µg/m³", "icon": "mdi:smog", "device_class": None},
    "o3": {"unit": "µg/m³", "icon": "mdi:molecule", "device_class": SensorDeviceClass.OZONE},
    "co": {"unit": "mg/m³", "icon": "mdi:molecule-co", "device_class": SensorDeviceClass.CO},
    "ch4": {"unit": "mg/m³", "icon": "mdi:molecule", "device_class": None},
    "nmhc": {"unit": "mg/m³", "icon": "mdi:molecule", "device_class": None},
    "thc": {"unit": "mg/m³", "icon": "mdi:molecule", "device_class": None},
    "c6h6": {"unit": "µg/m³", "icon": "mdi:molecule", "device_class": None},
    "c7h8": {"unit": "µg/m³", "icon": "mdi:molecule", "device_class": None},
    "c8h0": {"unit": "µg/m³", "icon": "mdi:molecule", "device_class": None},
    "c4h6": {"unit": "µg/m³", "icon": "mdi:molecule", "device_class": None},
    "h2s": {"unit": "µg/m³", "icon": "mdi:scent", "device_class": None},
    "temp": {"unit": "°C", "icon": "mdi:thermometer", "device_class": SensorDeviceClass.TEMPERATURE},
    "pres": {"unit": "hPa", "icon": "mdi:gauge", "device_class": SensorDeviceClass.ATMOSPHERIC_PRESSURE},
    "humi": {"unit": "%", "icon": "mdi:water-percent", "device_class": SensorDeviceClass.HUMIDITY},
    "wind_speed": {"unit": "m/s", "icon": "mdi:weather-windy", "device_class": SensorDeviceClass.WIND_SPEED},
    "wind_direction_name": {"unit": None, "icon": "mdi:compass", "device_class": None},
}

# Calendar Binary Sensor Definitions
BINARY_SENSOR_TYPES = {
    "fire": {"icon": "mdi:fire"},
    "smell": {"icon": "mdi:scent"},
    "noise": {"icon": "mdi:volume-high"},
    "water": {"icon": "mdi:water"},
    "smoke": {"icon": "mdi:smoke"},
    "work": {"icon": "mdi:wrench"},
}
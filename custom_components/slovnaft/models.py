"""Data models for the Sused Slovnaft integration."""
from dataclasses import dataclass
from typing import Optional

@dataclass
class CalendarDayStatus:
    date_timestamp: int
    fire: bool
    smell: bool
    noise: bool
    water: bool
    smoke: bool
    work: bool

@dataclass
class StationAirQuality:
    site_number: str
    timestamp: int
    pm10: Optional[float]
    pm25: Optional[float]
    so2: Optional[float]
    no: Optional[float]
    no2: Optional[float]
    nox: Optional[float]
    o3: Optional[float]
    co: Optional[float]
    ch4: Optional[float]
    nmhc: Optional[float]
    thc: Optional[float]
    c6h6: Optional[float]
    c7h8: Optional[float]
    c8h0: Optional[float]
    c4h6: Optional[float]
    h2s: Optional[float]
    temp: Optional[float]
    pres: Optional[float]
    humi: Optional[float]
    glrd: Optional[float]
    filt: Optional[float]
    wind_direction_name: Optional[str]
    wind_speed: Optional[float]
    wind_degrees: Optional[float]
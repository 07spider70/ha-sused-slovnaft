"""Data models for the Sused Slovnaft integration."""
from dataclasses import dataclass
from typing import Optional, Dict
import homeassistant.util.dt as dt_util

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
class CalendarData:
    days: Dict[int, CalendarDayStatus]
    notes_by_month: Dict[str, Optional[str]]

    def _get_note_for_offset(self, month_offset: int) -> Optional[str]:
        """Helper to safely fetch a note offset from the real-time current month."""
        now = dt_util.now()
        y, m = now.year, now.month + month_offset
        if m < 1:
            y -= 1
            m += 12
        elif m > 12:
            y += 1
            m -= 12
        return self.notes_by_month.get(f"{y}-{m:02d}")

    @property
    def last_month_note(self) -> Optional[str]:
        return self._get_note_for_offset(-1)

    @property
    def this_month_note(self) -> Optional[str]:
        return self._get_note_for_offset(0)

    @property
    def next_month_note(self) -> Optional[str]:
        return self._get_note_for_offset(1)

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
"""API Client for the Sused Slovnaft integration."""
import re
import html
import asyncio
import logging
import socket
from typing import Any, Dict, Optional

import aiohttp
import homeassistant.util.dt as dt_util

from .const import CALENDAR_ENDPOINT, ENV_ENDPOINT
from .models import CalendarDayStatus, StationAirQuality, CalendarData

_LOGGER = logging.getLogger(__name__)


class SlovnaftApiError(Exception):
    pass


class SlovnaftConnectionError(SlovnaftApiError):
    pass


class SlovnaftDataError(SlovnaftApiError):
    pass


class SlovnaftApiClient:
    def __init__(self, session: aiohttp.ClientSession, request_timeout: int = 10) -> None:
        self._session = session
        self._timeout = request_timeout

    async def _api_wrapper(self, method: str, url: str, data: dict = None, headers: dict = None) -> Any:
        try:
            async with asyncio.timeout(self._timeout):
                response = await self._session.request(method=method, url=url, data=data, headers=headers)
                response.raise_for_status()
                json_data = await response.json()
                _LOGGER.debug("Received response from %s: %s bytes", url, len(str(json_data)))
                return json_data
        except asyncio.TimeoutError as err:
            raise SlovnaftConnectionError(f"Timeout connecting to {url}") from err
        except (aiohttp.ClientError, socket.gaierror) as err:
            raise SlovnaftConnectionError(f"Error connecting to {url}: {err}") from err
        except Exception as err:
            raise SlovnaftApiError(f"Unexpected error from {url}: {err}") from err

    async def get_calendar(self) -> CalendarData:
        now = dt_util.now()
        _LOGGER.debug("Fetching calendar data for %d-%02d", now.year, now.month)
        url = f"{CALENDAR_ENDPOINT}/{now.year}-{now.month}"
        raw_data = await self._api_wrapper("GET", url, headers={"Accept": "application/json"})

        def _clean_html(raw_html: Optional[str]) -> Optional[str]:
            """Helper to strip HTML tags and unescape characters."""
            if not raw_html:
                return None
            text = raw_html.replace("</p>", "\n").replace("<br>", "\n").replace("<br/>", "\n")
            text = re.sub('<.*?>', '', text)
            text = html.unescape(text)
            return "\n".join([line.strip() for line in text.splitlines() if line.strip()])

        try:
            parsed_days = {}
            for month_key in ["lastMonth", "thisMonth", "nextMonth"]:
                for day_data in raw_data.get(month_key, []):
                    attrs = day_data.get("attributes", {})
                    timestamp = int(day_data.get("date", 0))
                    is_edited = str(day_data.get("edited", "0")) == "1"
                    parsed_days[timestamp] = CalendarDayStatus(
                        date_timestamp=timestamp,
                        fire=bool(attrs.get("fire", 0)),
                        smell=bool(attrs.get("smell", 0)),
                        noise=bool(attrs.get("noise", 0)),
                        water=bool(attrs.get("water", 0)),
                        smoke=bool(attrs.get("smoke", 0)),
                        work=bool(attrs.get("work", 0)),
                        edited=is_edited,
                        note=_clean_html(day_data.get("note")) if day_data.get("note") else None,
                    )

            def get_month_key(y: int, m: int) -> str:
                if m < 1:
                    return f"{y - 1}-12"
                elif m > 12:
                    return f"{y + 1}-01"
                return f"{y}-{m:02d}"

            # Map the HTML text to absolute YYYY-MM strings
            notes_by_month = {
                get_month_key(now.year, now.month - 1): _clean_html(raw_data.get("lastMonthNote")),
                get_month_key(now.year, now.month): _clean_html(raw_data.get("thisMonthNote")),
                get_month_key(now.year, now.month + 1): _clean_html(raw_data.get("nextMonthNote")),
            }

            _LOGGER.debug("Successfully parsed calendar data for %d days", len(parsed_days))
            return CalendarData(
                days=parsed_days,
                notes_by_month=notes_by_month,
            )
        except (KeyError, TypeError, ValueError) as err:
            raise SlovnaftDataError(f"Failed to parse calendar data: {err}") from err

    async def get_environment(self) -> Dict[str, StationAirQuality]:
        _LOGGER.debug("Fetching environment data...")
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        raw_data = await self._api_wrapper("POST", ENV_ENDPOINT, data={"updated_at": "0"}, headers=headers)

        try:
            stations = {}

            def _parse_float(val: Any) -> Optional[float]:
                if val is None or val == "":
                    return None
                try:
                    return float(val)
                except ValueError:
                    return None

            for env in raw_data.get("environment", []):
                site_id = str(env.get("site_number"))
                if not site_id:
                    continue

                stations[site_id] = StationAirQuality(
                    site_number=site_id,
                    timestamp=int(env.get("timestamp", 0)),
                    pm10=_parse_float(env.get("pm10")),
                    pm25=_parse_float(env.get("pm25")),
                    so2=_parse_float(env.get("so2")),
                    no=_parse_float(env.get("no")),
                    no2=_parse_float(env.get("no2")),
                    nox=_parse_float(env.get("nox")),
                    o3=_parse_float(env.get("o3")),
                    co=_parse_float(env.get("co")),
                    ch4=_parse_float(env.get("ch4")),
                    nmhc=_parse_float(env.get("nmhc")),
                    thc=_parse_float(env.get("thc")),
                    c6h6=_parse_float(env.get("c6h6")),
                    c7h8=_parse_float(env.get("c7h8")),
                    c8h0=_parse_float(env.get("c8h0")),
                    c4h6=_parse_float(env.get("c4h6")),
                    h2s=_parse_float(env.get("h2s")),
                    temp=_parse_float(env.get("temp")),
                    pres=_parse_float(env.get("pres")),
                    humi=_parse_float(env.get("humi")),
                    glrd=_parse_float(env.get("glrd")),
                    filt=_parse_float(env.get("filt")),
                    wind_direction_name=None,
                    wind_speed=_parse_float(env.get("wv")),
                    wind_degrees=_parse_float(env.get("wd"))
                )

            for wind in raw_data.get("wind", []):
                site_id = str(wind.get("station"))
                if site_id in stations:
                    stations[site_id].wind_direction_name = wind.get("direction")
                    if wind.get("speed"):
                        stations[site_id].wind_speed = _parse_float(wind.get("speed"))
                    if wind.get("degrees"):
                        stations[site_id].wind_degrees = _parse_float(wind.get("degrees"))
            _LOGGER.debug("Successfully parsed environment data for %s stations", len(stations))
            return stations
        except (KeyError, TypeError, ValueError) as err:
            raise SlovnaftDataError(f"Failed to parse environment: {err}") from err
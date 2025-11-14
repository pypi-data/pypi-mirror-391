from __future__ import annotations

from typing import Literal, Optional, List
from .base import WABaseModel, Location
from .forecast import Astro, DayWeather, HourWeather


class MarineTide(WABaseModel):
    """Информация об одном приливе/отливе."""
    tide_time: str
    tide_height_mt: float
    tide_type: Literal["High", "Low"]


class MarineDay(WABaseModel):
    """Морская погода на один день (с волнами, приливами и т.п.)."""
    date: str
    date_epoch: int
    day: DayWeather
    astro: Astro
    tide: List[MarineTide]
    hour: List[MarineHourWeather]


class MarineForecast(WABaseModel):
    """Контейнер с морским прогнозом."""
    forecastday: List[MarineDay]

class MarineResponse(WABaseModel):
    location: Location
    forecast: MarineForecast

class MarineHourWeather(WABaseModel):
    time_epoch: int
    time: str
    temp_c: float
    temp_f: float
    wind_mph: float
    wind_kph: float
    wind_degree: int
    wind_dir: str
    pressure_mb: float
    pressure_in: float
    humidity: int
    cloud: int
    vis_km: float
    vis_miles: float
    gust_mph: float
    gust_kph: float

    water_temp_c: Optional[float] = None
    water_temp_f: Optional[float] = None
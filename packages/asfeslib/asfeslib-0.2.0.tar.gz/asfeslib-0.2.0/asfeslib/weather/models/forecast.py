from __future__ import annotations

from typing import List, Optional, Union
from .base import WABaseModel, Condition
from pydantic import Field, field_validator


class Astro(WABaseModel):
    """Астрономические данные: солнце и луна."""
    sunrise: str
    sunset: str
    moonrise: str
    moonset: str
    moon_phase: str
    moon_illumination: Union[str, int] = Field(default="")
    is_moon_up: Optional[int] = None
    is_sun_up: Optional[int] = None
    
    @field_validator("moon_illumination")
    def _to_str(cls, v):
        return str(v)


class HourWeather(WABaseModel):
    """Почасовой прогноз/история погоды."""
    time_epoch: int
    time: str
    temp_c: float
    temp_f: float
    condition: Condition
    wind_mph: float
    wind_kph: float
    wind_degree: int
    wind_dir: str
    pressure_mb: float
    pressure_in: float
    precip_mm: float
    precip_in: float
    humidity: int
    cloud: int
    feelslike_c: float
    feelslike_f: float
    windchill_c: float
    windchill_f: float
    heatindex_c: float
    heatindex_f: float
    dewpoint_c: float
    dewpoint_f: float
    will_it_rain: int
    will_it_snow: int
    is_day: int
    vis_km: float
    vis_miles: float
    chance_of_rain: int
    chance_of_snow: int
    gust_mph: float
    gust_kph: float


class DayWeather(WABaseModel):
    """Сводка за день (макс/мин/средняя температура и т.п.)."""
    maxtemp_c: float
    maxtemp_f: float
    mintemp_c: float
    mintemp_f: float
    avgtemp_c: float
    avgtemp_f: float
    maxwind_mph: float
    maxwind_kph: float
    totalprecip_mm: float
    totalprecip_in: float
    avgvis_km: float
    avgvis_miles: float
    avghumidity: int
    condition: Condition
    uv: float


class ForecastDay(WABaseModel):
    """Прогноз/история на один день."""
    date: str
    date_epoch: int
    day: DayWeather
    astro: Astro
    hour: List[HourWeather]


class Forecast(WABaseModel):
    """Контейнер с прогнозом на несколько дней."""
    forecastday: List[ForecastDay]

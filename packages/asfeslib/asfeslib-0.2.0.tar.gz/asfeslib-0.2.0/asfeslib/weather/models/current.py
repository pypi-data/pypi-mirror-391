from __future__ import annotations

from typing import Optional
from .base import WABaseModel, Condition


class CurrentWeather(WABaseModel):
    """Текущая (реальная) погода по данным WeatherAPI."""
    last_updated: str
    last_updated_epoch: int
    temp_c: float
    temp_f: float
    feelslike_c: float
    feelslike_f: float
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
    is_day: int
    uv: float
    gust_mph: float
    gust_kph: float
    condition: Condition

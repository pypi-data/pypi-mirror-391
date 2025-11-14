from __future__ import annotations

from typing import Optional
from pydantic import BaseModel


class WABaseModel(BaseModel):
    """Базовая модель для всех схем WeatherAPI."""
    model_config = {
        "extra": "ignore",
        "populate_by_name": True,
        "str_strip_whitespace": True,
    }


class Condition(WABaseModel):
    """Условие погоды (описание, иконка, код)."""
    text: str
    icon: str
    code: int


class Location(WABaseModel):
    """Модель локации, которая возвращается во всех основных API."""
    name: str
    region: str
    country: str
    lat: float
    lon: float
    tz_id: str
    localtime_epoch: int
    localtime: str
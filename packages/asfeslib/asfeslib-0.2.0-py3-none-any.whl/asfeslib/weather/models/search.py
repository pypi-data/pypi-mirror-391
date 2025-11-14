from __future__ import annotations

from typing import Optional
from .base import WABaseModel


class SearchResult(WABaseModel):
    """Результат поиска/автодополнения локаций."""
    id: Optional[int] = None
    name: str
    region: str
    country: str
    lat: float
    lon: float
    url: Optional[str] = None

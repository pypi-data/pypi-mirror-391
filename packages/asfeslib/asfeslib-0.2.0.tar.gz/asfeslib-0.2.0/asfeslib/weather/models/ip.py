from __future__ import annotations

from .base import WABaseModel

class IPResponse(WABaseModel):
    ip: str
    type: str
    continent_code: str
    continent_name: str
    country_code: str
    country_name: str
    is_eu: bool
    geoname_id: int | None = None
    city: str
    region: str
    lat: float
    lon: float
    tz_id: str
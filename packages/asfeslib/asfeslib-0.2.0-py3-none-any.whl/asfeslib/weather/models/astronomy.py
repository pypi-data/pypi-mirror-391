from __future__ import annotations
from .base import WABaseModel, Location
from .forecast import Astro


class AstronomyData(WABaseModel):
    astro: Astro

class AstronomyResponse(WABaseModel):
    location: Location
    astronomy: AstronomyData

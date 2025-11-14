from __future__ import annotations

from .base import WABaseModel, Location


class TimezoneResponse(WABaseModel):
    """Ответ Timezone API."""
    location: Location

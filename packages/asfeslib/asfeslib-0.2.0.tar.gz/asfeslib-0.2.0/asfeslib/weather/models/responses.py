from __future__ import annotations

from typing import Optional, List
from .base import WABaseModel, Location
from .current import CurrentWeather
from .forecast import Forecast
from .alerts import Alerts
from .marine import MarineForecast
from .ip import IPResponse
from .timezone import TimezoneResponse as _Timezone
from .search import SearchResult
from .bulk import BulkResponse as _BulkResponse


class CurrentResponse(WABaseModel):
    """Ответ для current.json."""
    location: Location
    current: CurrentWeather


class ForecastResponse(WABaseModel):
    """Ответ для forecast.json."""
    location: Location
    current: CurrentWeather
    forecast: Forecast
    alerts: Optional[Alerts] = None


class HistoryResponse(WABaseModel):
    """Ответ для history.json."""
    location: Location
    forecast: Forecast


class FutureResponse(WABaseModel):
    """Ответ для future.json."""
    location: Location
    forecast: Forecast


class AlertsResponse(WABaseModel):
    """Ответ для alerts.json (обёртка, чтобы тип возвращаемый был явным)."""
    alerts: Alerts


class TimezoneResult(_Timezone):
    """Уточнённый алиас для результата Timezone API."""
    ...


class BulkResult(_BulkResponse):
    """Алиас для результата Bulk API."""
    ...

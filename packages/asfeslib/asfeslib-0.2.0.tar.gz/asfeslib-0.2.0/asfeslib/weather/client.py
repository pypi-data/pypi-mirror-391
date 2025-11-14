from __future__ import annotations

from typing import List, Optional, Sequence

import httpx

from .models import (
    Location,
    CurrentWeather,
    Forecast,
    Alerts,
    MarineForecast,
    SearchResult,
    IPResponse,
    BulkLocationRequest,
    BulkQuery,
    CurrentResponse,
    ForecastResponse,
    MarineResponse,
    AlertsResponse,
    TimezoneResult,
    BulkResult,
)
from .models.forecast import Astro
from .models.responses import HistoryResponse, FutureResponse
from .models.timezone import TimezoneResponse
from .models.astronomy import AstronomyResponse
from .models.bulk import BulkResponse



class WeatherApiClient:
    """
    Async-клиент для WeatherAPI (v1).

    Использование:

        client = WeatherApiClient(api_key="...", lang="ru")
        async with client:
            res = await client.current("Moscow")
            print(res.current.temp_c)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.weatherapi.com/v1",
        timeout: float = 10.0,
        lang: Optional[str] = None,
    ) -> None:
        """
        Параметры:
        api_key: API-ключ WeatherAPI.
        base_url: базовый URL API (по умолчанию https://api.weatherapi.com/v1).
        timeout: таймаут HTTP-запросов в секундах.
        lang: код языка (например, 'ru', 'en', 'de'), если нужно получать текст условий погоды на языке.
        """
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._lang = lang
        self._client: Optional[httpx.AsyncClient] = None


    async def __aenter__(self) -> "WeatherApiClient":
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout,
            params={"key": self._api_key},
        )
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
                params={"key": self._api_key},
            )
        return self._client

    async def aclose(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None


    def _build_params(self, extra: Optional[dict] = None) -> dict:
        params: dict = {}
        if self._lang:
            params["lang"] = self._lang
        if extra:
            params.update(extra)
        return params

    async def _get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        resp = await self.client.get(endpoint, params=self._build_params(params))
        resp.raise_for_status()
        return resp.json()

    async def _post(self, endpoint: str, params: Optional[dict] = None, json: Optional[dict] = None) -> dict:
        resp = await self.client.post(
            endpoint,
            params=self._build_params(params),
            json=json,
        )
        resp.raise_for_status()
        return resp.json()


    async def current(self, q: str) -> CurrentResponse:
        """
        Получить текущую (реальную) погоду для указанной локации.

        Параметры:
        q: строка локации (город, координаты, индекс, 'auto:ip', и т.п.).

        Возвращает:
        CurrentResponse: модель с полями location и current.
        """
        data = await self._get("current.json", {"q": q})
        return CurrentResponse(
            location=Location(**data["location"]),
            current=CurrentWeather(**data["current"]),
        )


    async def forecast(
        self,
        q: str,
        days: int = 1,
        alerts: bool = False,
        aqi: bool = False,
    ) -> ForecastResponse:
        """
        Получить прогноз погоды на несколько дней.

        Параметры:
        q: строка локации (город, координаты и т.п.).
        days: количество дней прогноза (1–14).
        alerts: включать ли предупреждения (alerts=yes).
        aqi: включать ли данные по качеству воздуха (aqi=yes).

        Возвращает:
        ForecastResponse: location, current, forecast и необязательный alerts.
        """
        params = {
            "q": q,
            "days": days,
            "alerts": "yes" if alerts else "no",
            "aqi": "yes" if aqi else "no",
        }
        data = await self._get("forecast.json", params)
        alerts_obj = None
        if "alerts" in data and data["alerts"]:
            alerts_obj = Alerts(**data["alerts"])
        return ForecastResponse(
            location=Location(**data["location"]),
            current=CurrentWeather(**data["current"]),
            forecast=Forecast(**data["forecast"]),
            alerts=alerts_obj,
        )


    async def history(
        self,
        q: str,
        dt: str,
        end_dt: Optional[str] = None,
        aqi: bool = False,
    ) -> HistoryResponse:
        """
        Получить исторические данные погоды за дату или диапазон.

        Параметры:
        q: строка локации.
        dt: начальная дата в формате YYYY-MM-DD (>= 2010-01-01).
        end_dt: конечная дата (максимум +30 дней к dt) — доступно в Pro+.
        aqi: включать ли данные по качеству воздуха.

        Возвращает:
        HistoryResponse: location и forecast (Forecast).
        """
        params: dict = {"q": q, "dt": dt, "aqi": "yes" if aqi else "no"}
        if end_dt:
            params["end_dt"] = end_dt
        data = await self._get("history.json", params)
        return HistoryResponse(
            location=Location(**data["location"]),
            forecast=Forecast(**data["forecast"]),
        )


    async def future(self, q: str, dt: str) -> FutureResponse:
        """
        Получить прогноз погоды для даты в будущем (14–300 дней от текущей даты).

        Параметры:
        q: строка локации.
        dt: дата в будущем (YYYY-MM-DD).

        Возвращает:
        FutureResponse: location и forecast.
        """
        params = {"q": q, "dt": dt}
        data = await self._get("future.json", params)
        return FutureResponse(
            location=Location(**data["location"]),
            forecast=Forecast(**data["forecast"]),
        )


    async def search(self, q: str) -> List[SearchResult]:
        """
        Поиск/автодополнение локаций.

        Параметры:
        q: часть названия города/локации.

        Возвращает:
        список SearchResult с координатами и информацией.
        """
        data = await self._get("search.json", {"q": q})
        return [SearchResult(**item) for item in data]


    async def alerts(self, q: str) -> AlertsResponse:
        """
        Получить погодные предупреждения для локации.

        Параметры:
        q: строка локации.

        Возвращает:
        AlertsResponse с полем alerts (список предупреждений).
        """
        data = await self._get("alerts.json", {"q": q})
        alerts_obj = Alerts(**data.get("alerts", {"alert": []}))
        return AlertsResponse(alerts=alerts_obj)


    async def marine(self, q: str, days: int = 3) -> MarineResponse:
        """
        Получить морской прогноз (волны, ветер, приливы и т.д.).

        Параметры:
        q: строка локации (координаты моря/океана).
        days: количество дней (до 7, в зависимости от тарифа).

        Возвращает:
        MarineResponse: location и forecast (MarineForecast).
        """
        data = await self._get("marine.json", {"q": q, "days": days})
        return MarineResponse(
            location=Location(**data["location"]),
            forecast=MarineForecast(**data["forecast"]),
        )


    async def astronomy(self, q: str, dt: str) -> AstronomyResponse:
        """
        Получить астрономические данные (восход/закат, фаза луны и т.д.) для даты.

        Параметры:
        q: строка локации.
        dt: дата в формате YYYY-MM-DD.

        Возвращает:
        AstronomyResponse: объект с полями location и astronomy.astro.
        """
        data = await self._get("astronomy.json", {"q": q, "dt": dt})
        return AstronomyResponse(**data)


    async def timezone(self, q: str) -> TimezoneResult:
        """
        Получить информацию о часовом поясе и локальном времени.

        Параметры:
        q: строка локации (город, координаты, IP и т.п.).

        Возвращает:
        TimezoneResult: объект с location, содержащим tz_id и локальное время.
        """
        data = await self._get("timezone.json", {"q": q})
        return TimezoneResult(location=Location(**data["location"]))


    async def ip_lookup(self, q: str) -> IPResponse:
        """
        Определить геолокацию и часовой пояс по IP.

        Параметры:
        ip: IP-адрес (IPv4/IPv6) или 'auto:ip' для автоопределения.

        Возвращает:
        IPResult: информация о стране, городе, координатах и tz_id.
        """
        data = await self._get("ip.json", {"q": q})
        return IPResponse(**data)

    async def bulk_current(
        self,
        locations: Sequence[BulkLocationRequest],
    ) -> BulkResult:
        """
        Bulk-запрос текущей погоды для нескольких локаций за один HTTP-запрос.

        Параметры:
        locations: последовательность BulkLocationRequest с полями q и custom_id.

        Возвращает:
        BulkResult: контейнер с полем bulk, внутри которого по одному объекту на каждую локацию.
        """
        body = BulkQuery(locations=list(locations))
        data = await self._post(
            "current.json",
            params={"q": "bulk"},
            json=body.model_dump(),
        )
        return BulkResult(**data)
    
    async def bulk(self, locations: list[dict]) -> BulkResponse:
        """
        Bulk API: получение погоды сразу по нескольким городам.
        """
        body = {"locations": locations}
        data = await self._post(
            "current.json",
            params={"q": "bulk"},
            json=body,
        )
        return BulkResponse(**data)
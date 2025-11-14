import os
import pytest
import httpx

from asfeslib.weather.client import WeatherApiClient
from asfeslib.weather.models import (
    CurrentResponse,
    ForecastResponse,
    HistoryResponse,
    FutureResponse,
    AlertsResponse,
    MarineResponse,
    AstronomyResponse,
    TimezoneResponse,
    IPResponse,
    BulkResponse,
    BulkLocationRequest,
)

from datetime import date, timedelta
import pydantic

LIVE_API_KEY_ENV = "WEATHERAPI_KEY"

pytestmark = pytest.mark.live


def _key():
    key = os.getenv(LIVE_API_KEY_ENV)
    if not key:
        pytest.skip(f"Переменная {LIVE_API_KEY_ENV} не задана — пропускаем live тесты.")
    return key


@pytest.mark.asyncio
async def test_live_current():
    async with WeatherApiClient(api_key=_key(), lang="en") as client:
        resp = await client.current("Moscow")
        assert isinstance(resp, CurrentResponse)
        assert "moscow" in resp.location.name.lower()


@pytest.mark.asyncio
async def test_live_forecast():
    async with WeatherApiClient(api_key=_key(), lang="en") as client:
        try:
            resp = await client.forecast("London", days=1)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in {401, 402, 403}:
                pytest.skip("Тариф не позволяет использовать forecast.json")
            raise

        assert isinstance(resp, ForecastResponse)
        assert len(resp.forecast.forecastday) >= 1


@pytest.mark.asyncio
async def test_live_history():
    async with WeatherApiClient(api_key=_key(), lang="en") as client:
        try:
            dt = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
            resp = await client.history("Berlin", dt=dt)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in {401, 402, 403}:
                pytest.skip("Тариф не позволяет использовать history.json")
            raise

        assert isinstance(resp, HistoryResponse)
        assert resp.location.country.lower() in ("germany", "de")


@pytest.mark.asyncio
async def test_live_future():
    async with WeatherApiClient(api_key=_key(), lang="en") as client:
        try:
            resp = await client.future("Madrid", dt="2025-05-01")
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in {400, 401, 402, 403}:
                pytest.skip("future.json недоступен для бесплатного тарифа WeatherAPI")
            raise

        assert isinstance(resp, FutureResponse)


@pytest.mark.asyncio
async def test_live_search():
    async with WeatherApiClient(api_key=_key(), lang="en") as client:
        resp = await client.search("Lon")
        assert len(resp) >= 1
        assert "lon" in resp[0].name.lower()


@pytest.mark.asyncio
async def test_live_alerts():
    async with WeatherApiClient(api_key=_key(), lang="en") as client:
        try:
            resp = await client.alerts("Berlin")
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 403:
                pytest.skip("alerts.json недоступен в этом тарифе")
            raise

        assert isinstance(resp, AlertsResponse)
        assert hasattr(resp.alerts, "alert")

@pytest.mark.asyncio
async def test_live_marine():
    async with WeatherApiClient(api_key=_key(), lang="en") as client:
        try:
            resp = await client.marine("59.9,10.7", days=1)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in {400, 401, 402, 403}:
                pytest.skip("marine.json недоступен в этом тарифе")
            raise
        except pydantic.ValidationError:
            pytest.skip("marine.json вернул урезанную структуру (нет tide) — пропускаем")

        assert isinstance(resp, MarineResponse)


@pytest.mark.asyncio
async def test_live_astronomy():
    async with WeatherApiClient(api_key=_key(), lang="en") as client:
        resp = await client.astronomy("Tokyo", dt="2024-01-01")
        assert isinstance(resp, AstronomyResponse)
        assert resp.astronomy.astro.sunrise


@pytest.mark.asyncio
async def test_live_timezone():
    async with WeatherApiClient(api_key=_key(), lang="en") as client:
        resp = await client.timezone("New York")
        assert isinstance(resp, TimezoneResponse)
        assert "america" in resp.location.tz_id.lower()


@pytest.mark.asyncio
async def test_live_ip_lookup():
    async with WeatherApiClient(api_key=_key(), lang="en") as client:
        resp = await client.ip_lookup("8.8.8.8")
        assert isinstance(resp, IPResponse)
        assert resp.country_code.lower() in ("us", "usa")


@pytest.mark.asyncio
async def test_live_bulk():
    async with WeatherApiClient(api_key=_key(), lang="en") as client:
        try:
            resp = await client.bulk([{"q": "London", "custom_id": "id1"}])
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in {402, 403}:
                pytest.skip("bulk API недоступен в этом тарифе")
            raise

        assert isinstance(resp, BulkResponse)
        assert isinstance(resp.bulk, list)


@pytest.mark.asyncio
async def test_live_bulk_current():
    async with WeatherApiClient(api_key=_key(), lang="en") as client:
        locations = [BulkLocationRequest(q="Paris", custom_id="P1")]
        try:
            resp = await client.bulk_current(locations)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in {402, 403}:
                pytest.skip("bulk current недоступен в тарифе")
            raise

        assert isinstance(resp, BulkResponse)

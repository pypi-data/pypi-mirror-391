import pytest
import httpx
from asfeslib.weather.models import TimezoneResponse


@pytest.mark.asyncio
async def test_weather_timezone(weather_client, mock_transport_factory):
    async def handler(request):
        assert request.url.path.endswith("/timezone.json")

        return httpx.Response(
            200,
            json={
                "location": {
                    "name": "NYC",
                    "region": "NY",
                    "country": "USA",
                    "lat": 40.7,
                    "lon": -74.0,
                    "tz_id": "America/New_York",
                    "localtime_epoch": 12345,
                    "localtime": "2025-01-01 08:00"
                }
            }
        )

    transport = mock_transport_factory(handler)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="https://api.weatherapi.com/v1"
    ) as mock_client:
        weather_client._client = mock_client

        resp = await weather_client.timezone("NYC")

        assert isinstance(resp, TimezoneResponse)
        assert resp.location.tz_id == "America/New_York"
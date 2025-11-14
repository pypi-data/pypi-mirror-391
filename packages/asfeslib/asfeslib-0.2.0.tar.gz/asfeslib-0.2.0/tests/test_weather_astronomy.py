import pytest
import httpx
from asfeslib.weather.models import AstronomyResponse


@pytest.mark.asyncio
async def test_weather_astronomy(weather_client, mock_transport_factory):
    async def handler(request):
        assert request.url.path.endswith("/astronomy.json")
        return httpx.Response(
            200,
            json={
                "location": {
                    "name": "Tokyo",
                    "region": "",
                    "country": "Japan",
                    "lat": 35.6,
                    "lon": 139.7,
                    "tz_id": "Asia/Tokyo",
                    "localtime_epoch": 100,
                    "localtime": "2025-01-01 12:00"
                },
                "astronomy": {
                    "astro": {
                        "sunrise": "06:40",
                        "sunset": "16:40",
                        "moonrise": "02:00",
                        "moonset": "13:00",
                        "moon_phase": "New",
                        "moon_illumination": "0"
                    }
                }
            }
        )

    transport = mock_transport_factory(handler)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="https://api.weatherapi.com/v1"
    ) as mock_client:
        weather_client._client = mock_client

        resp = await weather_client.astronomy("Tokyo", dt="2025-01-01")

        assert isinstance(resp, AstronomyResponse)
        assert resp.astronomy.astro.sunrise == "06:40"
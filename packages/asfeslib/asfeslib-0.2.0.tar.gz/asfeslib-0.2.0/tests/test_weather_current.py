import pytest
import httpx
from asfeslib.weather.client import WeatherApiClient
from asfeslib.weather.models import CurrentResponse


@pytest.mark.asyncio
async def test_weather_current(weather_client, mock_transport_factory):
    async def handler(request):
        assert request.url.path.endswith("/current.json")
        return httpx.Response(
            200,
            json={
                "location": {
                    "name": "Moscow",
                    "region": "",
                    "country": "Russia",
                    "lat": 55.75,
                    "lon": 37.61,
                    "tz_id": "Europe/Moscow",
                    "localtime_epoch": 123456,
                    "localtime": "2025-01-01 12:00"
                },
                "current": {
                    "last_updated": "2025-01-01 12:00",
                    "last_updated_epoch": 111,
                    "temp_c": 5.0,
                    "temp_f": 41.0,
                    "feelslike_c": 3.0,
                    "feelslike_f": 37.4,
                    "wind_mph": 10,
                    "wind_kph": 16,
                    "wind_degree": 240,
                    "wind_dir": "WSW",
                    "pressure_mb": 1010,
                    "pressure_in": 29.8,
                    "precip_mm": 0.0,
                    "precip_in": 0.0,
                    "humidity": 50,
                    "cloud": 20,
                    "is_day": 1,
                    "uv": 1.0,
                    "gust_mph": 15,
                    "gust_kph": 24,
                    "condition": {
                        "text": "Clear",
                        "icon": "//icon.png",
                        "code": 1000
                    }
                }
            }
        )

    transport = mock_transport_factory(handler)
    async with httpx.AsyncClient(transport=transport, base_url="https://api.weatherapi.com/v1") as mock_client:
        weather_client._client = mock_client
        result = await weather_client.current("Moscow")

        assert isinstance(result, CurrentResponse)
        assert result.location.name == "Moscow"
        assert result.current.temp_c == 5.0

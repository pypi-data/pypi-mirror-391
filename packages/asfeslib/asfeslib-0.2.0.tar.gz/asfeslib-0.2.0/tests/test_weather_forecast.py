import pytest
import httpx
from asfeslib.weather.models import ForecastResponse


@pytest.mark.asyncio
async def test_weather_forecast(weather_client, mock_transport_factory):
    async def handler(request):
        assert request.url.path.endswith("/forecast.json")
        return httpx.Response(
            200,
            json={
                "location": {
                    "name": "Moscow", "region": "", "country": "Russia",
                    "lat": 55.75, "lon": 37.61,
                    "tz_id": "Europe/Moscow",
                    "localtime_epoch": 111, "localtime": "2025-01-01 12:00"
                },
                "current": {
                    "last_updated": "2025-01-01 12:00",
                    "last_updated_epoch": 111,
                    "temp_c": 1.0, "temp_f": 33.8,
                    "feelslike_c": -1.0, "feelslike_f": 30.2,
                    "wind_mph": 5, "wind_kph": 8, "wind_degree": 250,
                    "wind_dir": "WSW",
                    "pressure_mb": 1000, "pressure_in": 29.5,
                    "precip_mm": 0, "precip_in": 0,
                    "humidity": 60, "cloud": 20, "is_day": 1,
                    "uv": 1.0, "gust_mph": 8, "gust_kph": 13,
                    "condition": {"text": "Sunny", "icon": "//icon.png", "code": 1000}
                },
                "forecast": {
                    "forecastday": [
                        {
                            "date": "2025-01-01",
                            "date_epoch": 111,
                            "day": {
                                "maxtemp_c": 2, "maxtemp_f": 35.6,
                                "mintemp_c": -3, "mintemp_f": 26.6,
                                "avgtemp_c": 0,
                                "avgtemp_f": 32,
                                "maxwind_mph": 10,
                                "maxwind_kph": 16,
                                "totalprecip_mm": 0,
                                "totalprecip_in": 0,
                                "avgvis_km": 10,
                                "avgvis_miles": 6,
                                "avghumidity": 65,
                                "condition": {"text": "Sunny", "icon": "//icon.png", "code": 1000},
                                "uv": 1.0
                            },
                            "astro": {
                                "sunrise": "08:00", "sunset": "16:00",
                                "moonrise": "10:00", "moonset": "20:00",
                                "moon_phase": "Waxing",
                                "moon_illumination": "50"
                            },
                            "hour": []
                        }
                    ]
                },
                "alerts": {"alert": []}
            }
        )

    transport = mock_transport_factory(handler)
    async with httpx.AsyncClient(transport=transport, base_url="https://api.weatherapi.com/v1") as mock_client:
        weather_client._client = mock_client
        result = await weather_client.forecast("Moscow", days=1)

        assert isinstance(result, ForecastResponse)
        assert result.location.name == "Moscow"
        assert len(result.forecast.forecastday) == 1

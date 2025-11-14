import pytest
import httpx
from asfeslib.weather.models import MarineResponse


@pytest.mark.asyncio
async def test_weather_marine(weather_client, mock_transport_factory):
    async def handler(request):
        assert request.url.path.endswith("/marine.json")

        return httpx.Response(
            200,
            json={
                "location": {
                    "name": "Oslo",
                    "region": "",
                    "country": "Norway",
                    "lat": 59.9,
                    "lon": 10.7,
                    "tz_id": "Europe/Oslo",
                    "localtime_epoch": 123,
                    "localtime": "2025-01-01 12:00"
                },
                "forecast": {
                    "forecastday": [
                        {
                            "date": "2025-01-01",
                            "date_epoch": 123,
                            "day": {
                                "maxtemp_c": 3,
                                "maxtemp_f": 37,
                                "mintemp_c": -1,
                                "mintemp_f": 30,
                                "avgtemp_c": 1,
                                "avgtemp_f": 33,
                                "maxwind_mph": 20,
                                "maxwind_kph": 32,
                                "totalprecip_mm": 1,
                                "totalprecip_in": 0.03,
                                "avgvis_km": 7,
                                "avgvis_miles": 4,
                                "avghumidity": 80,
                                "condition": {"text": "Cloudy", "icon": "//i.png", "code": 1006},
                                "uv": 0.5
                            },
                            "astro": {
                                "sunrise": "09:00",
                                "sunset": "15:00",
                                "moonrise": "11:00",
                                "moonset": "23:00",
                                "moon_phase": "Full",
                                "moon_illumination": "95",
                            },
                            "tide": [
                                {"tide_time": "10:00", "tide_height_mt": 0.5, "tide_type": "High"}
                            ],
                            "hour": []
                        }
                    ]
                }
            }
        )

    transport = mock_transport_factory(handler)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="https://api.weatherapi.com/v1"
    ) as mock_client:
        weather_client._client = mock_client

        resp = await weather_client.marine("59.9,10.7", days=1)

        assert isinstance(resp, MarineResponse)
        assert resp.location.country == "Norway"
        assert resp.forecast.forecastday[0].tide[0].tide_type == "High"
import pytest
import httpx
from asfeslib.weather.models import FutureResponse


@pytest.mark.asyncio
async def test_weather_future(weather_client, mock_transport_factory):
    async def handler(request):
        assert request.url.path.endswith("/future.json")
        assert b"dt=2025-05-01" in request.url.query

        return httpx.Response(
            200,
            json={
                "location": {
                    "name": "Madrid",
                    "region": "",
                    "country": "Spain",
                    "lat": 40.4,
                    "lon": -3.7,
                    "tz_id": "Europe/Madrid",
                    "localtime_epoch": 123,
                    "localtime": "2025-05-01 10:00"
                },
                "forecast": {
                    "forecastday": [
                        {
                            "date": "2025-05-01",
                            "date_epoch": 123,
                            "day": {
                                "maxtemp_c": 25,
                                "maxtemp_f": 77,
                                "mintemp_c": 15,
                                "mintemp_f": 59,
                                "avgtemp_c": 20,
                                "avgtemp_f": 68,
                                "maxwind_mph": 12,
                                "maxwind_kph": 19,
                                "totalprecip_mm": 0,
                                "totalprecip_in": 0,
                                "avgvis_km": 10,
                                "avgvis_miles": 6,
                                "avghumidity": 50,
                                "condition": {"text": "Sunny", "icon": "//i.png", "code": 1000},
                                "uv": 6.0
                            },
                            "astro": {
                                "sunrise": "07:00", "sunset": "21:00",
                                "moonrise": "03:00", "moonset": "15:00",
                                "moon_phase": "New",
                                "moon_illumination": "0"
                            },
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
        resp = await weather_client.future("Madrid", dt="2025-05-01")

        assert isinstance(resp, FutureResponse)
        assert resp.location.name == "Madrid"
        assert resp.forecast.forecastday[0].day.maxtemp_c == 25
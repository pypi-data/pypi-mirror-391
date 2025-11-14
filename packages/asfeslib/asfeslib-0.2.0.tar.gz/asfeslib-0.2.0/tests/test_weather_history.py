import pytest
import httpx
from asfeslib.weather.models import HistoryResponse


@pytest.mark.asyncio
async def test_weather_history(weather_client, mock_transport_factory):
    async def handler(request):
        assert request.url.path.endswith("/history.json")
        assert b"dt=2025-01-01" in request.url.query

        return httpx.Response(
            200,
            json={
                "location": {
                    "name": "Berlin",
                    "region": "",
                    "country": "Germany",
                    "lat": 52.52,
                    "lon": 13.4,
                    "tz_id": "Europe/Berlin",
                    "localtime_epoch": 111,
                    "localtime": "2025-01-02 12:00",
                },
                "forecast": {
                    "forecastday": [
                        {
                            "date": "2025-01-01",
                            "date_epoch": 111,
                            "day": {
                                "maxtemp_c": 4,
                                "maxtemp_f": 39,
                                "mintemp_c": -1,
                                "mintemp_f": 30,
                                "avgtemp_c": 2,
                                "avgtemp_f": 35.6,
                                "maxwind_mph": 10,
                                "maxwind_kph": 16,
                                "totalprecip_mm": 0,
                                "totalprecip_in": 0,
                                "avgvis_km": 8,
                                "avgvis_miles": 5,
                                "avghumidity": 70,
                                "condition": {"text": "Sunny", "icon": "//i.png", "code": 1000},
                                "uv": 1.5
                            },
                            "astro": {
                                "sunrise": "08:00", "sunset": "16:00",
                                "moonrise": "10:00", "moonset": "20:00",
                                "moon_phase": "Full",
                                "moon_illumination": "90"
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
        resp = await weather_client.history("Berlin", dt="2025-01-01")

        assert isinstance(resp, HistoryResponse)
        assert resp.location.country == "Germany"
        assert resp.forecast.forecastday[0].date == "2025-01-01"

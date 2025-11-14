import pytest
import httpx
from asfeslib.weather.models import BulkResponse


@pytest.mark.asyncio
async def test_weather_bulk(weather_client, mock_transport_factory):
    async def handler(request):
        assert request.url.path.endswith("/current.json")
        assert b"q=bulk" in request.url.query

        return httpx.Response(
            200,
            json={
                "bulk": [
                    {
                        "query": {
                            "custom_id": "id1",
                            "q": "London",
                            "location": {
                                "name": "London",
                                "region": "",
                                "country": "UK",
                                "lat": 51.5,
                                "lon": -0.12,
                                "tz_id": "Europe/London",
                                "localtime_epoch": 123,
                                "localtime": "2025-01-01 10:00"
                            },
                            "current": {
                                "last_updated": "2025-01-01",
                                "last_updated_epoch": 100,
                                "temp_c": 10,
                                "temp_f": 50,
                                "feelslike_c": 8,
                                "feelslike_f": 46.4,
                                "wind_mph": 5,
                                "wind_kph": 8,
                                "wind_degree": 250,
                                "wind_dir": "W",
                                "pressure_mb": 1012,
                                "pressure_in": 29.8,
                                "precip_mm": 0,
                                "precip_in": 0,
                                "humidity": 60,
                                "cloud": 10,
                                "is_day": 1,
                                "uv": 2.0,
                                "gust_mph": 7,
                                "gust_kph": 12,
                                "condition": {
                                    "text": "Clear",
                                    "icon": "//clear.png",
                                    "code": 1000
                                }
                            }
                        }
                    }
                ]
            }
        )

    transport = mock_transport_factory(handler)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="https://api.weatherapi.com/v1"
    ) as mock_client:
        weather_client._client = mock_client

        resp = await weather_client.bulk(
            [{"q": "London", "custom_id": "id1"}]
        )

        assert isinstance(resp, BulkResponse)
        assert resp.bulk[0].query["custom_id"] == "id1"
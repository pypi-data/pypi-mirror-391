import pytest
import httpx
from asfeslib.weather.models import IPResponse


@pytest.mark.asyncio
async def test_weather_ip(weather_client, mock_transport_factory):
    async def handler(request):
        assert request.url.path.endswith("/ip.json")

        return httpx.Response(
            200,
            json={
                "ip": "8.8.8.8",
                "type": "ipv4",
                "continent_code": "NA",
                "continent_name": "North America",
                "country_code": "US",
                "country_name": "United States",
                "is_eu": False,
                "geoname_id": 123,
                "city": "Mountain View",
                "region": "California",
                "lat": 37.4,
                "lon": -122.0,
                "tz_id": "America/Los_Angeles"
            }
        )

    transport = mock_transport_factory(handler)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="https://api.weatherapi.com/v1"
    ) as mock_client:
        weather_client._client = mock_client

        resp = await weather_client.ip_lookup("8.8.8.8")

        assert isinstance(resp, IPResponse)
        assert resp.city == "Mountain View"
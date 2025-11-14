import pytest
import httpx
from asfeslib.weather.models import SearchResult


@pytest.mark.asyncio
async def test_weather_search(weather_client, mock_transport_factory):
    async def handler(request):
        assert request.url.path.endswith("/search.json")

        return httpx.Response(
            200,
            json=[
                {
                    "id": 123,
                    "name": "London",
                    "region": "City of London",
                    "country": "UK",
                    "lat": 51.5,
                    "lon": -0.12,
                    "url": "london"
                }
            ]
        )

    transport = mock_transport_factory(handler)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="https://api.weatherapi.com/v1"
    ) as mock_client:
        weather_client._client = mock_client

        results = await weather_client.search("Lon")

        assert len(results) == 1
        assert isinstance(results[0], SearchResult)
        assert results[0].country == "UK"
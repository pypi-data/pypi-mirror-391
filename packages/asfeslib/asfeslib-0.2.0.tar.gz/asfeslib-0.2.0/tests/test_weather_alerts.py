import pytest
import httpx
from asfeslib.weather.models import AlertsResponse


@pytest.mark.asyncio
async def test_weather_alerts(weather_client, mock_transport_factory):
    async def handler(request):
        assert request.url.path.endswith("/alerts.json")

        return httpx.Response(
            200,
            json={
                "alerts": {
                    "alert": [
                        {
                            "headline": "Storm Warning",
                            "msgtype": "Alert",
                            "severity": "Severe",
                            "urgency": "Immediate",
                            "areas": "North",
                            "category": "Met",
                            "certainty": "Likely",
                            "event": "Storm",
                            "note": "Strong winds expected",
                            "effective": "2025-01-01",
                            "expires": "2025-01-02",
                            "desc": "Dangerous wind",
                            "instruction": "Stay inside"
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

        resp = await weather_client.alerts("Berlin")

        assert isinstance(resp, AlertsResponse)
        assert resp.alerts.alert[0].severity == "Severe"
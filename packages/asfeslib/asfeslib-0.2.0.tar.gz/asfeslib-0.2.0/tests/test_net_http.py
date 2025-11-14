import pytest
from asfeslib.net.http import HTTPClient
import asyncio


@pytest.mark.asyncio
async def test_http_get_json():
    async with HTTPClient(base_url="https://jsonplaceholder.typicode.com") as http:
        data = await http.get("/todos/1")
        assert isinstance(data, dict)
        assert data["id"] == 1


@pytest.mark.asyncio
async def test_http_404_handling():
    async with HTTPClient(base_url="https://jsonplaceholder.typicode.com") as http:
        res = await http.get("/nonexistent")
        assert res is None

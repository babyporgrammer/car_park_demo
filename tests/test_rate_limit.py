# tests/test_rate_limit.py
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

transport = ASGITransport(app=app)
headers = {"X-API-Key": "cxy"}

@pytest.mark.asyncio
async def test_nearby_rate_limit():
    """
    Test the rate limit for the nearby car parks endpoint.
    :return: if the rate limit is exceeded, it should return a 429 status code.
    """
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # assume the rate limit is 30 requests per minute
        for i in range(31):
            resp = await ac.get("/carparks/nearby?lat=0&lng=0", headers=headers)
        assert resp.status_code == 429

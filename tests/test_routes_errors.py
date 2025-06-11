# tests/test_routes_errors.py
import pytest
from httpx import AsyncClient, ASGITransport
from main import app
import api.routes

VALID_API_KEY = "cxy"
headers = {"X-API-Key": VALID_API_KEY}
transport = ASGITransport(app=app)

@pytest.mark.no_rate_limit
@pytest.mark.asyncio
async def test_carpark_detail_bad_format(monkeypatch):
    async def fake_detail(_):
        return {"spots": "x", "occupancy": {"total": "y"}, "location": {}}
    monkeypatch.setattr("api.routes.fetch_facility_detail", fake_detail, raising=True)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/carparks/any", headers=headers)
        assert resp.status_code == 500

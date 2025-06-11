import pytest
from httpx import AsyncClient, ASGITransport
from main import app

VALID_API_KEY = "cxy"
INVALID_API_KEY = "wrong-key"
headers = {"X-API-Key": VALID_API_KEY}
bad_headers = {"X-API-Key": INVALID_API_KEY}

transport = ASGITransport(app=app)
@pytest.mark.no_rate_limit
@pytest.fixture(autouse=True)
def inject_api_key(monkeypatch):
    monkeypatch.setenv("TFNSW_API_KEY", "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJDVWtRN2p1VktqT1Jtdll3TUpGa2dwTDB2Vm1VSmpRSEFpYjNlaGU3bFYwIiwiaWF0IjoxNzQ5NTk5OTE0fQ._Tr-ONWVwB-vY26HrGLLqx1KuxIfbsU5lr6-h8KL7gc")
@pytest.mark.no_rate_limit
@pytest.mark.asyncio
async def test_ping_authorized():
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/carparks/ping", headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Car Park API is running."

@pytest.mark.no_rate_limit
@pytest.mark.asyncio
async def test_ping_unauthorized():
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/carparks/ping", headers=bad_headers)
        assert response.status_code == 401

@pytest.mark.no_rate_limit
@pytest.mark.asyncio
async def test_nearby_valid_radius():
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        params = {"lat": -33.7, "lng": 150.9, "radius_km": 10}
        response = await ac.get("/carparks/nearby", headers=headers, params=params)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            first = data[0]
            assert "facility_id" in first
            assert "available_spots" in first
            assert first["distance_km"] <= 10

@pytest.mark.no_rate_limit
@pytest.mark.asyncio
async def test_facility_detail_valid():
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/carparks/26", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["facility_id"] == "26"
        assert "available_spots" in data
        assert "status" in data
        assert data["status"] in ["Available", "Almost Full", "Full"]

@pytest.mark.no_rate_limit
@pytest.mark.asyncio
async def test_facility_detail_invalid_id():
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/carparks/invalid999", headers=headers)
        assert response.status_code in (404, 500)

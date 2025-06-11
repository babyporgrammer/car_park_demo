# tests/test_carpark_service.py
import pytest
import respx
import httpx
from services.carpark_service import fetch_facility_ids, fetch_facility_detail, cache

TFNSW_BASE = "https://api.transport.nsw.gov.au/v1/carpark"

@pytest.mark.asyncio
@respx.mock
@pytest.mark.no_rate_limit
async def test_fetch_facility_ids_success():
    """
    Test fetching facility IDs successfully and caching the result.
    :return: the list of facility IDs.
    """
    facility_data = {"1": {}, "2": {}}
    respx.get(TFNSW_BASE).respond(json=facility_data, status_code=200)
    cache.clear()
    ids = await fetch_facility_ids()
    assert ids == ["1", "2"]
    ids2 = await fetch_facility_ids()
    assert ids2 == ids

@pytest.mark.asyncio
@respx.mock
@pytest.mark.no_rate_limit
async def test_fetch_facility_ids_http_error():
    """
    Test handling HTTP errors when fetching facility IDs.
    :return: if the fetch fails, it should return an empty list.
    """
    respx.get(TFNSW_BASE).respond(status_code=500)
    cache.clear()
    ids = await fetch_facility_ids()
    assert ids == []

@pytest.mark.asyncio
@respx.mock
@pytest.mark.no_rate_limit
async def test_fetch_facility_detail_success_and_cache():
    """
    Test fetching facility detail successfully and caching the result.
    :return:  if the fetch is successful, it should return the facility detail.
    """
    facility_id = "123"
    url = f"{TFNSW_BASE}?facility={facility_id}"
    detail_payload = {"facility_id": facility_id, "spots": "10", "occupancy": {"total": "5"}, "location": {"latitude": "0","longitude":"0"}}
    respx.get(url).respond(json=detail_payload, status_code=200)
    cache.clear()
    detail = await fetch_facility_detail(facility_id)
    assert detail["facility_id"] == facility_id


    detail2 = await fetch_facility_detail(facility_id)
    assert detail2 == detail

@pytest.mark.no_rate_limit
"""
Test fetching facility detail with HTTP error handling.
:return: if the fetch fails, it should return None.
"""
def test_cache_expiry(monkeypatch):
    cache.set("facility_ids", ["a", "b"], expire=-1)


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
    # 准备 mock 返回一个 dict
    facility_data = {"1": {}, "2": {}}
    respx.get(TFNSW_BASE).respond(json=facility_data, status_code=200)

    # 首次调用，应走真实请求
    cache.clear()
    ids = await fetch_facility_ids()
    assert ids == ["1", "2"]

    # 再次调用，应命中缓存（不会再次触发 HTTP 请求）
    ids2 = await fetch_facility_ids()
    assert ids2 == ids

@pytest.mark.asyncio
@respx.mock
@pytest.mark.no_rate_limit
async def test_fetch_facility_ids_http_error():
    # 模拟 500 错误
    respx.get(TFNSW_BASE).respond(status_code=500)
    cache.clear()
    ids = await fetch_facility_ids()
    assert ids == []  # 错误分支返回空列表

@pytest.mark.asyncio
@respx.mock
@pytest.mark.no_rate_limit
async def test_fetch_facility_detail_success_and_cache():
    facility_id = "123"
    url = f"{TFNSW_BASE}?facility={facility_id}"
    detail_payload = {"facility_id": facility_id, "spots": "10", "occupancy": {"total": "5"}, "location": {"latitude": "0","longitude":"0"}}
    # 首次请求
    respx.get(url).respond(json=detail_payload, status_code=200)
    cache.clear()
    detail = await fetch_facility_detail(facility_id)
    assert detail["facility_id"] == facility_id

    # 第二次请求走缓存，不再触发 HTTP
    # 如果没有设置 mock，会抛异常
    detail2 = await fetch_facility_detail(facility_id)
    assert detail2 == detail

@pytest.mark.no_rate_limit
def test_cache_expiry(monkeypatch):
    # 预填缓存并设定过期时间已到
    cache.set("facility_ids", ["a", "b"], expire=-1)  # 立即过期
    # 然后再次调用 fetch_facility_ids，会重新发起 HTTP 请求（需配合 respx mock）


import httpx
from typing import List, Dict, Optional
import asyncio
from diskcache import Cache
from dotenv import load_dotenv
import os
load_dotenv()
# Initialize cache
cache = Cache(directory=".carpark_cache")

TFNSW_API_KEY = os.getenv("TFNSW_API_KEY")
if not TFNSW_API_KEY:
    raise RuntimeError("TFNSW_API_KEY environment variable is not set.")
TFNSW_BASE_URL = "https://api.transport.nsw.gov.au/v1/carpark"

headers = {
    "Authorization": f"apikey {TFNSW_API_KEY}"
}


async def fetch_facility_ids() -> List[str]:
    """
    get a list of all car park facility IDs.
    :return: list of facility IDs as strings.
    """
    if "facility_ids" in cache:
        print("Using cached facility IDs")
        return cache["facility_ids"]

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(TFNSW_BASE_URL, headers=headers)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict):
                facility_ids = list(data.keys())
                cache.set("facility_ids", facility_ids, expire=600)  # 缓存10分钟
                return facility_ids
    except httpx.HTTPError as e:
        print(f"Error fetching facility list: {e}")
    return []


async def fetch_facility_detail(facility_id: str) -> Optional[Dict]:
    """
    get detailed information for a specific car park facility by its ID.
    :param facility_id: int or str, the unique identifier for the car park facility.
    :return: returns a dictionary with detailed information about the car park facility,
    """
    key = f"facility:{facility_id}"
    if key in cache:
        #print(f"Using cached data for facility {facility_id}")
        return cache[key]

    url = f"{TFNSW_BASE_URL}?facility={facility_id}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            cache.set(key, data, expire=300)
            return data
    except httpx.HTTPError as e:
        print(f"Failed to fetch facility {facility_id}: {e}")
        return None


async def fetch_all_carparks() -> List[Dict]:
    """
    get detailed information for all car parks.
    """
    facility_ids = await fetch_facility_ids()
    print(f"Total facilities to fetch: {len(facility_ids)}")


    tasks = [fetch_facility_detail(fid) for fid in facility_ids]
    results = await asyncio.gather(*tasks)


    carparks = [r for r in results if r is not None]
    return carparks

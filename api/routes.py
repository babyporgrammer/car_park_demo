from fastapi import APIRouter, Query
from typing import List
from services.carpark_service import fetch_all_carparks,fetch_facility_detail
from schemas.response import CarParkSummary,CarParkDetail
from utils.haversine import haversine
from fastapi import HTTPException, Path
from api.dependencies import verify_api_key
from fastapi import Depends
from utils.rate_limit import limiter           # 关键：引入全局 limiter
from slowapi.util import get_remote_address
from fastapi import Request



router = APIRouter()

@router.get("/ping",dependencies=[Depends(verify_api_key)])
@limiter.limit("10/second")
async def ping(request: Request):
    return {"message": "Car Park API is running."}


@router.get("/nearby", response_model=List[CarParkSummary],dependencies=[Depends(verify_api_key)])
@limiter.limit("30/minute")   # 限制每分钟30次请求
async def get_nearby_carparks(
    request: Request,
    lat: float = Query(..., description="Your latitude"),
    lng: float = Query(..., description="Your longitude"),
    radius_km: float = Query(5, description="Search radius in kilometers"),
):
    """
    get nearby car parks within a specified radius from the given latitude and longitude.
    """
    carparks = await fetch_all_carparks()
    nearby = []

    for cp in carparks:
        try:
            facility_id = cp["facility_id"]
            name = cp["facility_name"]
            lat_cp = float(cp["location"]["latitude"])
            lng_cp = float(cp["location"]["longitude"])
            distance = haversine(lat, lng, lat_cp, lng_cp)
            if distance <= radius_km:
                total_spots = int(cp.get("spots", "0"))
                occupied = int(cp["occupancy"].get("total", "0"))
                available = total_spots - occupied
                nearby.append({
                    "facility_id": facility_id,
                    "name": name,
                    "latitude": lat_cp,
                    "longitude": lng_cp,
                    "distance_km": round(distance, 2),
                    "available_spots": max(available, 0)
                })
        except (KeyError, ValueError, TypeError):
            continue

    # sort by distance
    nearby.sort(key=lambda x: x["distance_km"])
    return nearby


@router.get("/{facility_id}", response_model=CarParkDetail,dependencies=[Depends(verify_api_key)])
@limiter.limit("90/minute")
async def get_carpark_detail(request: Request,
                             facility_id: str = Path(..., description="Car park facility ID")
                             ):
    """
    get detailed information about a specific car park by its facility ID.
    """
    data = await fetch_facility_detail(facility_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Facility not found")

    try:
        total_spots = int(data.get("spots", "0"))
        occupied = int(data["occupancy"].get("total", "0"))
        available = total_spots - occupied
        available = max(available, 0)
        lat_cp = float(data["location"]["latitude"])
        lng_cp = float(data["location"]["longitude"])
        updated = data.get("MessageDate")

        # 状态判定
        if available == 0:
            status = "Full"
        elif total_spots > 0 and available / total_spots < 0.1:
            status = "Almost Full"
        else:
            status = "Available"

        return {
            "facility_id": data["facility_id"],
            "name": data["facility_name"],
            "latitude": lat_cp,
            "longitude": lng_cp,
            "total_spots": total_spots,
            "occupied_spots": occupied,
            "available_spots": available,
            "status": status,
            "last_updated": updated
        }

    except (KeyError, ValueError, TypeError):
        raise HTTPException(status_code=500, detail="Invalid data format from TfNSW")
from pydantic import BaseModel
from datetime import datetime


class CarParkDetail(BaseModel):
    facility_id: str
    name: str
    latitude: float
    longitude: float
    total_spots: int
    occupied_spots: int
    available_spots: int
    status: str
    last_updated: datetime

class CarParkSummary(BaseModel):
    facility_id: str
    name: str
    latitude: float
    longitude: float
    distance_km: float
    available_spots: int

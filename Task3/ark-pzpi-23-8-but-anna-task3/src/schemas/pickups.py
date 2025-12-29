from pydantic import BaseModel
from datetime import datetime


class PickupCreate(BaseModel):
    scheduled_time: datetime
    container_site_id: int
    vehicle_id: int | None = None


class PickupUpdate(BaseModel):
    completed_time: datetime | None = None
    vehicle_id: int | None = None
    container_site_id: int


class PickupResponse(BaseModel):
    pickup_id: int
    scheduled_time: datetime
    completed_time: datetime | None = None
    container_site_id: int
    vehicle_id: int | None = None

    class Config:
        from_attributes = True


class PickupStatisticsResponse(BaseModel):
    total_pickups: int
    completed_pickups: int

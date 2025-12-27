from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class ContainerSiteBase(BaseModel):
    location_lat: str
    location_lng: str
    city: str | None = None
    street: str | None = None
    building: str | None = None
    entrance: str | None = None
    description: str | None = None


class ContainerSiteCreate(ContainerSiteBase):
    organization_id: int


class ContainerSiteUpdate(BaseModel):
    location_lat: str | None = None
    location_lng: str | None = None
    city: str | None = None
    street: str | None = None
    building: str | None = None
    entrance: str | None = None
    description: str | None = None


class ContainerSiteResponse(ContainerSiteBase):
    container_site_id: int
    organization_id: int

    class Config:
        orm_mode = True

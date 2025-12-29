from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class ContainerBase(BaseModel):
    type: str
    capacity: int
    fill_level: int | None = None
    status: str
    tilted: bool = False
    container_site_id: int


class ContainerCreate(ContainerBase):
    pass


class ContainerUpdate(BaseModel):
    type: str | None = None
    capacity: int | None = None
    fill_level: int | None = None
    status: str | None = None
    container_site_id: int | None = None


class ContainerResponse(ContainerBase):
    container_id: int
    last_update: datetime

    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    notification_id: int
    message: str
    message_type: str
    created_at: datetime
    container_site_id: Optional[int]

    class Config:
        from_attributes = True

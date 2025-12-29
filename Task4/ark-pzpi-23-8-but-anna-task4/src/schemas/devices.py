from pydantic import BaseModel
from datetime import datetime


class DeviceBase(BaseModel):
    device_name: str
    serial_number: str
    device_type: str | None = None
    container_id: int | None = None


class DeviceCreate(DeviceBase):
    battery_level: int | None = 100


class DeviceUpdate(BaseModel):
    device_name: str | None = None
    device_type: str | None = None
    container_id: int | None = None
    battery_level: int | None = None
    status: str | None = None


class DeviceResponse(DeviceBase):
    device_id: int
    battery_level: int | None = None
    status: str | None = None
    last_signal: datetime

    class Config:
        from_attributes = True


class DeviceTelemetry(BaseModel):
    serial_number: str
    fill_level: float
    temperature: float
    tilted: bool
    battery_level: int | None = None


class DeviceTelemetryView(BaseModel):
    serial_number: str
    battery_level: int
    last_signal: datetime

    fill_level: int | None = None
    temperature: float | None = None
    tilted: bool
    last_update: datetime

    class Config:
        from_attributes = True

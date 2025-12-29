from pydantic import BaseModel


class VehicleBase(BaseModel):
    vehicle_name: str
    number_plate: str


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(VehicleBase):
    pass


class VehicleResponse(VehicleBase):
    vehicle_id: int
    organization_id: int

    class Config:
        from_attributes = True

from pydantic import BaseModel
from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional


class ClientCompanyBase(BaseModel):
    name: str
    type: str | None = None
    city: str | None = None
    street: str | None = None
    building: str | None = None
    phone_number: str | None = None


class ClientCompanyCreate(ClientCompanyBase):
    email: EmailStr
    edrpou: str
    password: str


class ClientCompanyUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    city: str | None = None
    street: str | None = None
    building: str | None = None
    phone_number: str | None = None
    email: EmailStr | None = None
    edrpou: str | None = None
    password: str | None = None


class ClientCompanyResponse(ClientCompanyBase):
    client_id: int
    email: EmailStr
    edrpou: str

    class Config:
        from_attributes = True


class DisposalRequestCreate(BaseModel):
    waste_type: str
    waste_description: Optional[str] = None
    amount_kg: Optional[float] = None
    organization_id: int


class DisposalRequestResponse(BaseModel):
    request_id: int
    waste_type: str
    waste_description: Optional[str]
    amount_kg: Optional[float]
    status: str
    created_at: datetime
    organization_id: int
    client_id: int

    class Config:
        from_attributes = True

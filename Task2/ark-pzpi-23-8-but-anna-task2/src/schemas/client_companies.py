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

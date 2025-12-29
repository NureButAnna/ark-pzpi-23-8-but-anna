from pydantic import BaseModel
from pydantic import EmailStr


class OrganizationBase(BaseModel):
    name: str
    type: str | None = None
    city: str | None = None
    street: str | None = None
    building: str | None = None
    phone_number: str | None = None


class OrganizationCreate(OrganizationBase):
    email: EmailStr
    edrpou: str
    password: str


class OrganizationUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    city: str | None = None
    street: str | None = None
    building: str | None = None
    phone_number: str | None = None
    email: EmailStr | None = None
    edrpou: str | None = None
    password: str | None = None


class OrganizationResponse(OrganizationBase):
    organization_id: int
    email: EmailStr
    edrpou: str

    class Config:
        from_attributes = True

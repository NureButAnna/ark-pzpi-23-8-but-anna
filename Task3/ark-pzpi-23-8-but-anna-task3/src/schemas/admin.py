from pydantic import BaseModel, EmailStr
from typing import Optional


class AdminBase(BaseModel):
    last_name: str
    first_name: str
    patronymic: str | None = None
    email: EmailStr


class AdminCreate(AdminBase):
    password: str


class AdminUpdate(BaseModel):
    last_name: str | None = None
    first_name: str | None = None
    patronymic: str | None = None
    email:  EmailStr | None = None
    password: str | None = None


class AdminResponse(AdminBase):
    admin_id: int

    class Config:
        from_attributes = True

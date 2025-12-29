from pydantic import BaseModel, EmailStr
from typing import Literal


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    id: int
    email: EmailStr
    role: Literal["user", "client_company", "organization", "admin"]


class StatusUpdate(BaseModel):
    status: bool

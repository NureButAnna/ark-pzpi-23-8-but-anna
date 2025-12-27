from pydantic import BaseModel
from pydantic import EmailStr


class UserBase(BaseModel):
    last_name: str
    first_name: str
    patronymic: str | None = None
    phone_number: str | None = None
    email: EmailStr
    city: str | None = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    user_id: int

    class Config:
        from_attributes = True


class UserPublic(BaseModel):
    user_id: int
    email: EmailStr
    first_name: str
    last_name: str

    class Config:
        from_attributes = True

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.auth import get_current_user
from src.database import get_db
from src.models.users import Users
from src.schemas.users import UserCreate, UserResponse, UserPublic
from src.api.core import hash_password

router = APIRouter(
    prefix="/users",
    tags=["Users 👤"]
)


@router.post("/register", status_code=201)
def register_user(data: UserCreate, db: Session = Depends(get_db)):

    existing = db.query(Users).filter(Users.email == data.email).first()
    if existing:
        raise HTTPException(409, "User with this email already exists")

    hashed_password = hash_password(data.password)

    new_user = Users(
        first_name=data.first_name,
        last_name=data.last_name,
        patronymic=data.patronymic,
        email=data.email,
        phone_number=data.phone_number,
        city=data.city,
        password_hash=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    if role != "admin" and (
        role != "user" or entity.user_id != user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    user = db.query(Users).filter(Users.user_id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserCreate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    if role != "admin" and (
        role != "user" or entity.user_id != user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    user = db.query(Users).filter(Users.user_id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user

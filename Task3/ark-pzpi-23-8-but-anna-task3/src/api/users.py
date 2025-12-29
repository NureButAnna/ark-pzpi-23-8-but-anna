import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.models.notifications import Notifications
from src.models.container_sites import ContainerSite
from src.models.containers import Containers
from src.api.auth import get_current_user
from src.database import get_db
from src.models.users import Users
from src.schemas.users import UserCreate, UserResponse
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

    return {"message": "User registered successfully", "user_id": new_user.user_id}


@router.get(
    "/container-sites",
    summary="View container sites by user's city and waste type"
)
def get_container_sites(
    waste_type: str | None = None,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    user, role = current

    if role != "user":
        raise HTTPException(403, "Only users can view container sites")

    # місто береться з профілю користувача
    query = db.query(ContainerSite).filter(
        ContainerSite.city.ilike(user.city)
    )

    if waste_type:
        query = (
            query
            .join(
                Containers,
                Containers.container_site_id == ContainerSite.container_site_id
            )
            .filter(Containers.type.ilike(waste_type))
            .distinct()
        )

    sites = query.all()

    if not sites:
        raise HTTPException(
            status_code=404,
            detail="No container sites found for your request"
        )

    return sites


@router.get(
    "/containers/status",
    summary="View container fill levels by container sites"
)
def get_container_status(
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    user, role = current

    containers = (
        db.query(
            Containers.container_id.label("container_id"),
            Containers.type.label("container_type"),
            Containers.fill_level.label("fill_level"),
            ContainerSite.container_site_id.label("site_id"),
            ContainerSite.street.label("street"),
            ContainerSite.building.label("building"),
            ContainerSite.entrance.label("entrance")
        )
        .join(
            ContainerSite,
            Containers.container_site_id == ContainerSite.container_site_id
        )
        .filter(ContainerSite.city == user.city)
        .all()
    )

    return [
        {
            "container_id": c.container_id,
            "waste_type": c.container_type,
            "fill_level": c.fill_level,
            "container_site": {
                "site_id": c.site_id,
                "address": f"{c.street}, {c.building}" + (
                    f", підʼїзд {c.entrance}" if c.entrance else ""
                )
            }
        }
        for c in containers
    ]


@router.get(
    "/notifications/container-sites",
    summary="Notifications about new container sites in user's city"
)
def new_container_site_notifications(
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    user, role = current

    notifications = (
        db.query(Notifications)
        .join(
            ContainerSite,
            Notifications.container_site_id == ContainerSite.container_site_id
        )
        .filter(
            Notifications.message_type == "new_container_site",
            ContainerSite.city == user.city,
            Notifications.user_id == user.user_id
        )
        .order_by(Notifications.created_at.desc())
        .all()
    )

    return notifications


@router.get(
    "/notifications/collection",
    summary="Waste collection notifications for current user"
)
def waste_collection_notifications(
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    user, role = current

    return (
        db.query(Notifications)
        .filter(
            Notifications.user_id == user.user_id,
            Notifications.message_type == "waste_collection"
        )
        .order_by(Notifications.created_at.desc())
        .all()
    )


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

from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlalchemy import func
from datetime import date
from sqlalchemy.orm import Session

from src.models.users import Users
from src.models.notifications import Notifications
from src.database import get_db
from src.models.container_sites import ContainerSite
from src.models.pickups import Pickups
from src.schemas.pickups import PickupCreate, PickupResponse, PickupStatisticsResponse, PickupUpdate
from src.api.auth import get_current_user


router = APIRouter(
    prefix="/pickups",
    tags=["Pickups 🚚"]
)


@router.post("/", response_model=PickupResponse, status_code=201)
def create_pickup(
    data: PickupCreate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    if role not in ("admin", "organization"):
        raise HTTPException(403, "Access denied")

    containersite = (
        db.query(ContainerSite)
        .filter(ContainerSite.container_site_id == data.container_site_id)
        .first()
    )

    if not containersite:
        raise HTTPException(404, "Container site not found")

    pickup = Pickups(
        scheduled_time=data.scheduled_time,
        container_site_id=data.container_site_id,
        vehicle_id=data.vehicle_id
    )

    db.add(pickup)
    db.commit()
    db.refresh(pickup)

    users_in_city = (
        db.query(Users)
        .filter(Users.city == containersite.city)
        .all()
    )

    notifications = []

    for user in users_in_city:
        notifications.append(
            Notifications(
                user_id=user.user_id,
                container_site_id=containersite.container_site_id,
                message_type="waste_collection",
                message=(
                    f"Заплановано вивіз сміття за адресою "
                    f"{containersite.street} {containersite.building}"
                )
            )
        )

    db.add_all(notifications)
    db.commit()

    return pickup


@router.get("/", response_model=list[PickupResponse])
def get_pickups(
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    query = db.query(Pickups)

    if role == "organization":
        query = query.join(ContainerSite).filter(
            ContainerSite.organization_id == entity.organization_id
        )
    elif role != "admin":
        raise HTTPException(403, "Access denied")

    return query.all()


@router.put("/{pickup_id}", response_model=PickupResponse)
def update_pickup(
    pickup_id: int,
    data: PickupUpdate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    pickup = db.query(Pickups).filter(
        Pickups.pickup_id == pickup_id
    ).first()

    if not pickup:
        raise HTTPException(404, "Pickup not found")

    if role not in ("admin", "organization"):
        raise HTTPException(403, "Access denied")

    if data.completed_time is not None:
        pickup.completed_time = data.completed_time

    if data.vehicle_id is not None:
        pickup.vehicle_id = data.vehicle_id

    db.commit()
    db.refresh(pickup)

    return pickup


@router.delete("/{pickup_id}", status_code=204)
def delete_pickup(
    pickup_id: int,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    if role not in ("admin", "organization"):
        raise HTTPException(403, "Access denied")

    pickup = db.query(Pickups).filter(
        Pickups.pickup_id == pickup_id
    ).first()

    if not pickup:
        raise HTTPException(404, "Pickup not found")

    db.delete(pickup)
    db.commit()

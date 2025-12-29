from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.models.organization import Organization
from src.database import get_db
from src.models.vehicles import Vehicles
from src.schemas.vehicles import (
    VehicleCreate,
    VehicleUpdate,
    VehicleResponse
)
from src.api.auth import get_current_user
from src.models.users import Users

router = APIRouter(
    prefix="/vehicles",
    tags=["Vehicles 🚗"]
)


@router.post(
    "/",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED
)
def create_vehicle(
    data: VehicleCreate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    if role not in ("admin", "organization"):
        raise HTTPException(403, "Access denied")

    if role == "organization":
        organization_id = entity.organization_id
    else:
        if data.organization_id is None:
            raise HTTPException(
                status_code=400,
                detail="organization_id is required for admin"
            )
        organization_id = data.organization_id

    organization = (
        db.query(Organization)
        .filter(Organization.organization_id == organization_id)
        .first()
    )

    if not organization:
        raise HTTPException(
            status_code=404,
            detail=f"Organization with id={organization_id} not found"
        )

    vehicle = Vehicles(
        vehicle_name=data.vehicle_name,
        number_plate=data.number_plate,
        organization_id=organization_id
    )

    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

    return vehicle


@router.get("/", response_model=List[VehicleResponse])
def get_vehicles(
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    if role == "admin":
        return db.query(Vehicles).all()

    if role == "organization":
        return db.query(Vehicles).filter(
            Vehicles.organization_id == entity.organization_id
        ).all()

    raise HTTPException(403, "Access denied")


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    query = db.query(Vehicles).filter(
        Vehicles.vehicle_id == vehicle_id
    )

    if role == "organization":
        query = query.filter(
            Vehicles.organization_id == entity.organization_id
        )

    elif role != "admin":
        raise HTTPException(403, "Access denied")

    vehicle = query.first()

    if not vehicle:
        raise HTTPException(404, "Vehicle not found")

    return vehicle


@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: int,
    data: VehicleUpdate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    vehicle = db.query(Vehicles).filter(
        Vehicles.vehicle_id == vehicle_id
    ).first()

    if not vehicle:
        raise HTTPException(404, "Vehicle not found")

    if role == "organization" and \
       vehicle.organization_id != entity.organization_id:
        raise HTTPException(403, "Access denied")

    if role != "admin" and role != "organization":
        raise HTTPException(403, "Access denied")

    if data.vehicle_name is not None:
        vehicle.vehicle_name = data.vehicle_name

    if data.number_plate is not None:
        vehicle.number_plate = data.number_plate

    db.commit()
    db.refresh(vehicle)

    return vehicle


@router.delete(
    "/{vehicle_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    vehicle = db.query(Vehicles).filter(
        Vehicles.vehicle_id == vehicle_id
    ).first()

    if not vehicle:
        raise HTTPException(404, "Vehicle not found")

    if role == "organization" and \
       vehicle.organization_id != entity.organization_id:
        raise HTTPException(403, "Access denied")

    if role != "admin" and role != "organization":
        raise HTTPException(403, "Access denied")

    db.delete(vehicle)
    db.commit()

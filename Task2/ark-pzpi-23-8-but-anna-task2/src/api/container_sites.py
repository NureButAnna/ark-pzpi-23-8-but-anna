from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import exists
from sqlalchemy.orm import selectinload

from src.models.pickups import Pickups
from src.api.auth import get_current_user
from src.models.organization import Organization
from src.models.containers import Containers
from src.database import get_db
from src.models.container_sites import ContainerSite
from src.schemas.container_sites import (
    ContainerSiteCreate,
    ContainerSiteUpdate,
    ContainerSiteResponse
)

router = APIRouter(
    prefix="/container-sites",
    tags=["Container Sites 📍"]
)


@router.post("/", response_model=ContainerSiteResponse,
             status_code=status.HTTP_201_CREATED
             )
def create_container_site(
    data: ContainerSiteCreate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    if role not in ("admin", "organization"):
        raise HTTPException(403, "Access denied")

    if role == "organization" and data.organization_id != entity.organization_id:
        raise HTTPException(
            403,
            "You can create container sites only for your organization"
        )

    organization = (
        db.query(Organization)
        .filter(Organization.organization_id == data.organization_id)
        .first()
    )
    if not organization:
        raise HTTPException(404, "Organization not found")

    site = ContainerSite(**data.dict())
    db.add(site)
    db.commit()
    db.refresh(site)

    return site


@router.get("/", response_model=list[ContainerSiteResponse])
def get_container_sites(
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    if not current:
        return db.query(ContainerSite).all()

    entity, role = current

    if role != "organization":
        return db.query(ContainerSite).all()
    return (
        db.query(ContainerSite)
        .filter(ContainerSite.organization_id == entity.organization_id)
        .all()
    )


@router.get("/{container_site_id}", response_model=ContainerSiteResponse)
def get_container_site(
    container_site_id: int,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    site = (
        db.query(ContainerSite)
        .filter(ContainerSite.container_site_id == container_site_id)
        .first()
    )

    if not site:
        raise HTTPException(404, "Container site not found")

    if current:
        entity, role = current
        if role == "organization" and site.organization_id != entity.organization_id:
            raise HTTPException(403, "Access denied")

    return site


@router.put("/{container_site_id}", response_model=ContainerSiteResponse)
def update_container_site(
    container_site_id: int,
    data: ContainerSiteUpdate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    if role not in ("admin", "organization"):
        raise HTTPException(403, "Access denied")

    site = (
        db.query(ContainerSite)
        .filter(ContainerSite.container_site_id == container_site_id)
        .first()
    )

    if not site:
        raise HTTPException(404, "Container site not found")
    if role == "organization" and site.organization_id != entity.organization_id:
        raise HTTPException(403, "Access denied")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(site, field, value)

    db.commit()
    db.refresh(site)

    return site


@router.delete("/{container_site_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_container_site(
    container_site_id: int,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    if role not in ("admin", "organization"):
        raise HTTPException(403, "Access denied")

    site = (
        db.query(ContainerSite)
        .filter(ContainerSite.container_site_id == container_site_id)
        .first()
    )

    if not site:
        raise HTTPException(404, "Container site not found")
    if role == "organization" and site.organization_id != entity.organization_id:
        raise HTTPException(403, "Access denied")

    has_containers = db.query(
        exists().where(
            Containers.container_site_id == container_site_id
        )
    ).scalar()

    if has_containers:
        raise HTTPException(
            400,
            "Cannot delete container site: containers are attached"
        )

    has_pickups = db.query(
        exists().where(
            Pickups.container_site_id == container_site_id
        )
    ).scalar()

    if has_pickups:
        raise HTTPException(
            400,
            "Cannot delete container site: pickups are attached"
        )

    db.delete(site)
    db.commit()
    return {"message": "Container site deleted successfully"}

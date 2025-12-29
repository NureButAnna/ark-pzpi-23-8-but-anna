from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.models.users import Users
from src.database import get_db
from src.models.containers import Containers
from src.models.container_sites import ContainerSite
from src.schemas.containers import (
    ContainerCreate,
    ContainerUpdate,
    ContainerResponse
)
from src.api.auth import get_current_user

router = APIRouter(
    prefix="/containers",
    tags=["Containers 🗑️"]
)


@router.post("/", response_model=ContainerResponse, status_code=201)
def create_container(
    data: ContainerCreate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    if role not in ("admin", "organization"):
        raise HTTPException(403, "Access denied")

    site = db.query(ContainerSite).filter(
        ContainerSite.container_site_id == data.container_site_id
    ).first()

    if not site:
        raise HTTPException(404, "Container site not found")

    if role == "organization" and site.organization_id != entity.organization_id:
        raise HTTPException(
            403,
            "You can create containers only for your organization"
        )

    container = Containers(**data.dict())

    db.add(container)
    db.commit()
    db.refresh(container)

    return container


@router.get("/", response_model=list[ContainerResponse])
def get_containers(
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    if not current:
        return db.query(Containers).all()

    entity, role = current

    if role != "organization":
        return db.query(Containers).all()

    return (
        db.query(Containers)
        .join(ContainerSite)
        .filter(ContainerSite.organization_id == entity.organization_id)
        .all()
    )


@router.get("/{container_id}", response_model=ContainerResponse)
def get_container(
    container_id: int,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    container = (
        db.query(Containers)
        .join(ContainerSite)
        .filter(Containers.container_id == container_id)
        .first()
    )

    if not container:
        raise HTTPException(404, "Container not found")

    if not current:
        return container

    entity, role = current

    if role != "organization":
        return container

    if container.site.organization_id != entity.organization_id:
        raise HTTPException(403, "Access denied")

    return container


@router.put("/{container_id}", response_model=ContainerResponse)
def update_container(
    container_id: int,
    data: ContainerUpdate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    if role not in ("admin", "organization"):
        raise HTTPException(403, "Access denied")

    container = (
        db.query(Containers)
        .join(ContainerSite)
        .filter(Containers.container_id == container_id)
        .first()
    )

    if not container:
        raise HTTPException(404, "Container not found")

    if role == "organization" and \
       container.site.organization_id != entity.organization_id:
        raise HTTPException(403, "Access denied")

    update_data = data.dict(exclude_unset=True)

    if "container_site_id" in update_data:
        site = db.query(ContainerSite).filter(
            ContainerSite.container_site_id == update_data["container_site_id"]
        ).first()

        if not site:
            raise HTTPException(404, "Container site not found")

        if role == "organization" and site.organization_id != entity.organization_id:
            raise HTTPException(
                403,
                "You can move container only within your organization"
            )

    for field, value in update_data.items():
        setattr(container, field, value)

    db.commit()
    db.refresh(container)

    return container


@router.delete("/{container_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_container(
    container_id: int,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    if role not in ("admin", "organization"):
        raise HTTPException(403, "Access denied")

    container = (
        db.query(Containers)
        .join(ContainerSite)
        .filter(Containers.container_id == container_id)
        .first()
    )

    if not container:
        raise HTTPException(404, "Container not found")

    if role == "organization" and \
       container.site.organization_id != entity.organization_id:
        raise HTTPException(403, "Access denied")

    db.delete(container)
    db.commit()

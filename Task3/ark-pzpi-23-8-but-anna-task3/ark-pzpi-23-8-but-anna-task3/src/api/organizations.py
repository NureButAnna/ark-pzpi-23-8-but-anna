from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.auth import get_current_user
from src.database import get_db
from src.api.core import hash_password
from src.models.organization import Organization
from src.schemas.organizations import OrganizationCreate, OrganizationResponse, OrganizationUpdate
from src.models.disposal_requests import DisposalRequests

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations 🏢"]
)


@router.get("/", response_model=list[OrganizationResponse])
def get_organizations(db: Session = Depends(get_db)):
    return db.query(Organization).all()


@router.get("/{organization_id}", response_model=OrganizationResponse)
def get_organization(organization_id: int, db: Session = Depends(get_db)):

    org = db.query(Organization).filter(
        Organization.organization_id == organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found.")

    return org


@router.put("/{organization_id}", response_model=OrganizationResponse)
def update_organization(
    organization_id: int,
    data: OrganizationUpdate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    if role != "admin" and (
        role != "organization" or entity.organization_id != organization_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    org = (
        db.query(Organization)
        .filter(Organization.organization_id == organization_id)
        .first()
    )
    if not org:
        raise HTTPException(
            status_code=404,
            detail="Organization not found."
        )

    if data.email and data.email != org.email:
        exists = db.query(Organization).filter(
            Organization.email == data.email
        ).first()
        if exists:
            raise HTTPException(
                status_code=409,
                detail="Organization with this email already exists."
            )

    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(org, field, value)

    db.commit()
    db.refresh(org)

    return org

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.database import get_db
from src.api.auth import get_current_user
from src.models.client_companies import ClientCompanies
from src.models.disposal_requests import DisposalRequests
from src.models.organization import Organization
from src.schemas.client_companies import (
    DisposalRequestCreate,
    DisposalRequestResponse
)
from src.api.core import hash_password
from datetime import date, datetime

router = APIRouter(
    prefix="/requests",
    tags=["Requests 📥"]
)


@router.post(
    "/",
    response_model=DisposalRequestResponse,
    status_code=201
)
def create_disposal_request(
    data: DisposalRequestCreate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    if role not in ("client_company", "admin"):
        raise HTTPException(
            status_code=403,
            detail="Only client companies or admin can create disposal requests"
        )

    organization = db.query(Organization).filter(
        Organization.organization_id == data.organization_id
    ).first()

    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Organization not found"
        )

    client_id = entity.client_id if role == "client_company" else None

    new_request = DisposalRequests(
        waste_type=data.waste_type,
        waste_description=data.waste_description,
        amount_kg=data.amount_kg,
        status="pending",
        organization_id=data.organization_id,
        client_id=client_id
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return new_request


@router.get("/", response_model=list[DisposalRequestResponse])
def get_my_disposal_requests(
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    if role == "client_company":
        return db.query(DisposalRequests).filter(
            DisposalRequests.client_id == entity.client_id
        ).all()

    if role == "organization":
        return db.query(DisposalRequests).filter(
            DisposalRequests.organization_id == entity.organization_id
        ).all()

    if role == "admin":
        return db.query(DisposalRequests).all()

    raise HTTPException(403, "Access denied")


@router.put("/{request_id}/status", response_model=DisposalRequestResponse)
def update_disposal_request_status(
    request_id: int,
    status: str,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    if role not in ("organization", "admin"):
        raise HTTPException(403, "Access denied")

    request = db.query(DisposalRequests).filter(
        DisposalRequests.request_id == request_id
    ).first()

    if not request:
        raise HTTPException(404, "Request not found")

    request.status = status
    request.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(request)

    return request


@router.delete("/{request_id}", status_code=204)
def delete_disposal_request(
    request_id: int,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    request = db.query(DisposalRequests).filter(
        DisposalRequests.request_id == request_id
    ).first()

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Disposal request not found"
        )

    if role == "admin":
        db.delete(request)
        db.commit()
        return

    if role == "client_company":
        if request.client_id != entity.client_id:
            raise HTTPException(403, "Access denied")

        if request.status != "pending":
            raise HTTPException(
                status_code=409,
                detail="Only pending requests can be deleted"
            )

        db.delete(request)
        db.commit()
        return

    raise HTTPException(403, "Access denied")

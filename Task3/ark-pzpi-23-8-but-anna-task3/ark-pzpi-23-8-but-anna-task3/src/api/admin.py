from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import func
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from typing import List, Optional

from src.models.notifications import Notifications
from src.models.container_sites import ContainerSite
from src.models.containers import Containers
from src.schemas.organizations import OrganizationCreate, OrganizationResponse
from src.models.disposal_requests import DisposalRequests
from src.models.organization import Organization
from src.models.client_companies import ClientCompanies
from src.schemas.client_companies import ClientCompanyResponse
from src.models.users import Users
from src.schemas.users import UserResponse
from src.database import get_db
from src.api.auth import get_current_user
from src.models.admin import Admins
from src.schemas.auth import Token, MeResponse, StatusUpdate
from src.schemas.admin import AdminCreate, AdminResponse, AdminUpdate
from src.api.core import verify_password, hash_password, create_access_token, SECRET_KEY, ALGORITHM


router = APIRouter(
    prefix="/admin",
    tags=["Administration 🛠️"]
)

# User Management Endpoints


@router.get("/users", response_model=list[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    _, role = current

    if role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin can view all users"
        )

    return db.query(Users).all()


@router.patch("/users/{user_id}/status")
def patch_user_status(
    user_id: int,
    data: StatusUpdate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    _, role = current
    if role != "admin":
        raise HTTPException(403, "Only admin can change user status")

    user = db.query(Users).filter(Users.user_id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    user.status = data.status
    db.commit()

    return {
        "message": "Status updated",
        "user_id": user_id,
        "status": user.status
    }


@router.delete("/users/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    if role != "admin":
        raise HTTPException(403, "Only admin can delete users")

    user = db.query(Users).filter(Users.user_id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    db.delete(user)
    db.commit()


# Client Company Management Endpoints

@router.get("/client-companies", response_model=list[ClientCompanyResponse])
def get_all_client_companies(
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    if role != "admin":
        raise HTTPException(403, "Only admin can view all client companies")

    return db.query(ClientCompanies).all()


@router.patch("/client-companies/{client_id}/status")
def patch_client_company_status(
    client_id: int,
    data: StatusUpdate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    _, role = current
    if role != "admin":
        raise HTTPException(403, "Only admin can change company status")

    company = db.query(ClientCompanies).filter(
        ClientCompanies.client_id == client_id
    ).first()

    if not company:
        raise HTTPException(404, "Client company not found")

    company.status = data.status
    db.commit()

    return {
        "message": "Status updated",
        "client_id": client_id,
        "status": company.status
    }


@router.delete("/client-companies/{client_id}", status_code=204)
def delete_client_company(
    client_id: int,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    if role != "admin":
        raise HTTPException(403, "Only admin can delete client companies")

    company = db.query(ClientCompanies).filter(
        ClientCompanies.client_id == client_id
    ).first()

    if not company:
        raise HTTPException(404, "Client company not found")

    db.delete(company)
    db.commit()

# Organization Management Endpoints


@router.post(
    "/organizations",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_organization(
    data: OrganizationCreate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    _, role = current

    if role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin can create organizations"
        )

    if db.query(Organization).filter(Organization.email == data.email).first():
        raise HTTPException(
            status_code=409,
            detail="Organization with this email already exists."
        )

    if data.edrpou and db.query(Organization).filter(
        Organization.edrpou == data.edrpou
    ).first():
        raise HTTPException(
            status_code=409,
            detail="Organization with this EDRPOU already exists."
        )

    org_data = data.dict(exclude={"password"})
    org_data["password_hash"] = hash_password(data.password)

    org = Organization(**org_data)
    db.add(org)
    db.commit()
    db.refresh(org)

    return org


@router.patch("/organizations/{organization_id}/status")
def patch_organization_status(
    organization_id: int,
    data: StatusUpdate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    _, role = current
    if role != "admin":
        raise HTTPException(403, "Only admin can change organization status")

    org = db.query(Organization).filter(
        Organization.organization_id == organization_id
    ).first()

    if not org:
        raise HTTPException(404, "Organization not found")

    org.status = data.status
    db.commit()

    return {
        "message": "Status updated",
        "organization_id": organization_id,
        "status": org.status
    }


@router.delete("/organizations/{organization_id}", status_code=204)
def delete_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    if role != "admin":
        raise HTTPException(403, "Only admin can delete organizations")

    org = db.query(Organization).filter(
        Organization.organization_id == organization_id
    ).first()

    if not org:
        raise HTTPException(404, "Organization not found")

    if db.query(DisposalRequests).filter(
        DisposalRequests.organization_id == organization_id
    ).first():
        raise HTTPException(
            409,
            "Cannot delete organization: disposal requests exist"
        )

    db.delete(org)
    db.commit()

# Notification Management Endpoints


@router.get("/admin/notifications",
            summary="View notifications"
            )
def get_notifications(
    city: str | None = None,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    _, role = current
    if role != "admin":
        raise HTTPException(403, "Only admin can view notifications")

    query = (
        db.query(Notifications)
        .join(Users, Notifications.user_id == Users.user_id)
    )

    if city:
        query = query.filter(Users.city == city)

    return (
        query
        .order_by(Notifications.created_at.desc())
        .all()
    )


@router.delete(
    "/admin/notifications/{notification_id}",
    status_code=204,
    summary="Delete notification"
)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    _, role = current

    if role != "admin":
        raise HTTPException(403, "Only admin can delete notifications")

    notification = (
        db.query(Notifications)
        .filter(Notifications.notification_id == notification_id)
        .first()
    )

    if not notification:
        raise HTTPException(404, "Notification not found")

    db.delete(notification)
    db.commit()

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from typing import Optional

from src.database import get_db
from src.models.admin import Admins
from src.models.users import Users
from src.models.client_companies import ClientCompanies
from src.models.organization import Organization
from src.schemas.auth import Token, MeResponse
from src.schemas.users import UserResponse
from src.api.core import verify_password, hash_password, create_access_token, SECRET_KEY, ALGORITHM, oauth2_scheme


router = APIRouter(
    prefix="/auth",
    tags=["Authentication 🔐"]
)


@router.post("/login", response_model=Token, summary="Login and get JWT token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    email = form_data.username

    user = db.query(Users).filter(Users.email == email).first()
    if user and verify_password(form_data.password, user.password_hash):
        token = create_access_token({
            "sub": str(user.user_id),
            "role": "user"
        })
        return {"access_token": token, "token_type": "bearer"}

    company = db.query(ClientCompanies).filter(
        ClientCompanies.email == email
    ).first()
    if company and verify_password(form_data.password, company.password_hash):
        token = create_access_token({
            "sub": str(company.client_id),
            "role": "client_company"
        })
        return {"access_token": token, "token_type": "bearer"}

    organization = db.query(Organization).filter(
        Organization.email == email
    ).first()
    if organization and verify_password(form_data.password, organization.password_hash):
        token = create_access_token({
            "sub": str(organization.organization_id),
            "role": "organization"
        })
        return {"access_token": token, "token_type": "bearer"}

    admin = db.query(Admins).filter(Admins.email == email).first()
    if admin and verify_password(form_data.password, admin.password_hash):
        token = create_access_token({
            "sub": str(admin.admin_id),
            "role": "admin"
        })
        return {"access_token": token, "token_type": "bearer"}

    raise HTTPException(status_code=401, detail="Incorrect email or password")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    cred_exc = HTTPException(
        status_code=401,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        entity_id = payload.get("sub")
        role = payload.get("role")

        if entity_id is None or role is None:
            raise cred_exc

    except JWTError:
        raise cred_exc

    if role == "user":
        identity = db.query(Users).filter(
            Users.user_id == int(entity_id)
        ).first()

    elif role == "client_company":
        identity = db.query(ClientCompanies).filter(
            ClientCompanies.client_id == int(entity_id)
        ).first()

    elif role == "organization":
        identity = db.query(Organization).filter(
            Organization.organization_id == int(entity_id)
        ).first()

    elif role == "admin":
        identity = db.query(Admins).filter(
            Admins.admin_id == int(entity_id)
        ).first()

    else:
        raise cred_exc

    if not identity:
        raise cred_exc

    return identity, role


@router.get("/me", response_model=MeResponse,
            summary="Get current user (requires token)"
            )
def read_me(data=Depends(get_current_user)):
    entity, role = data

    if role == "user":
        entity_id = entity.user_id
    elif role == "client_company":
        entity_id = entity.client_id
    elif role == "organization":
        entity_id = entity.organization_id
    elif role == "admin":
        entity_id = entity.admin_id
    else:
        raise HTTPException(400, "Unknown role")

    return {
        "id": entity_id,
        "email": entity.email,
        "role": role
    }

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.api.auth import get_current_user
from src.models.client_companies import ClientCompanies
from src.schemas.client_companies import (
    ClientCompanyCreate,
    ClientCompanyResponse,
    ClientCompanyUpdate
)
from src.api.core import hash_password


router = APIRouter(
    prefix="/client-companies",
    tags=["Client Companies 📝 "]
)


@router.post("/register", status_code=201)
def register_client_company(
    data: ClientCompanyCreate,
    db: Session = Depends(get_db)
):
    existing_email = db.query(ClientCompanies).filter(
        ClientCompanies.email == data.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=409,
            detail="Company with this email already exists."
        )

    existing_edrpou = db.query(ClientCompanies).filter(
        ClientCompanies.edrpou == data.edrpou
    ).first()

    if existing_edrpou:
        raise HTTPException(
            status_code=409,
            detail="Company with this EDRPOU already exists."
        )

    hashed_password = hash_password(data.password)

    new_company = ClientCompanies(
        name=data.name,
        type=data.type,
        city=data.city,
        street=data.street,
        building=data.building,
        phone_number=data.phone_number,
        email=data.email,
        password_hash=hashed_password,
        edrpou=data.edrpou
    )

    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    return {"message": "Client company registered successfully", "client_id": new_company.client_id}


@router.get("/{client_id}", response_model=ClientCompanyResponse)
def get_client_company(
    client_id: int,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    if role not in ("admin", "client_company"):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    # Компанія може переглядати тільки свій профіль
    if role == "client_company" and entity.client_id != client_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    company = db.query(ClientCompanies).filter(
        ClientCompanies.client_id == client_id
    ).first()

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Client company not found"
        )

    return company


@router.put("/{client_id}", response_model=ClientCompanyResponse)
def update_client_company(
    client_id: int,
    data: ClientCompanyUpdate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    if role not in ("admin", "client_company"):
        raise HTTPException(403, "Access denied")

    if role == "client_company" and entity.client_id != client_id:
        raise HTTPException(403, "Access denied")

    company = db.query(ClientCompanies).filter(
        ClientCompanies.client_id == client_id
    ).first()

    if not company:
        raise HTTPException(404, "Client company not found")

    update_data = data.dict(exclude_unset=True)

    if "email" in update_data:
        exists = db.query(ClientCompanies).filter(
            ClientCompanies.email == update_data["email"],
            ClientCompanies.client_id != client_id
        ).first()
        if exists:
            raise HTTPException(409, "Another company already uses this email")

    if "edrpou" in update_data:
        exists = db.query(ClientCompanies).filter(
            ClientCompanies.edrpou == update_data["edrpou"],
            ClientCompanies.client_id != client_id
        ).first()
        if exists:
            raise HTTPException(
                409, "Another company already uses this EDRPOU")

    if "password" in update_data:
        company.password_hash = hash_password(update_data.pop("password"))

    for key, value in update_data.items():
        setattr(company, key, value)

    db.commit()
    db.refresh(company)

    return company

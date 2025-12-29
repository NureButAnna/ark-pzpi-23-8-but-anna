from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Date, cast
from sqlalchemy.orm import Session

from src.models.disposal_requests import DisposalRequests
from src.models.container_sites import ContainerSite
from src.models.pickups import Pickups
from src.models.vehicles import Vehicles
from src.schemas.doc import WasteTransferActDTO
from src.database import get_db
from src.models import ClientCompanies, Organization
from src.api.auth import get_current_user
from datetime import date, datetime

router = APIRouter(
    prefix="/documents",
    tags=["Documents 📄"]
)


@router.get(
    "/waste-transfer-acts",
    response_model=list[WasteTransferActDTO],
    summary="View all waste transfer acts (generated dynamically)"
)
def get_all_waste_transfer_acts(
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    current_user, role = current

    query = db.query(DisposalRequests)

    if role == "admin":
        pass

    elif role == "organization":
        query = query.filter(
            DisposalRequests.organization_id ==
            current_user.organization_id
        )

    elif role == "client_company":
        query = query.filter(
            DisposalRequests.client_id ==
            current_user.client_id
        )

    else:
        raise HTTPException(403, "Access denied")

    requests = query.all()

    acts: list[WasteTransferActDTO] = []

    for r in requests:
        if not r.client or not r.organization:
            continue

        client = r.client
        organization = r.organization

        sender_address = (
            f"{client.city}, {client.street}, {client.building}"
        )
        receiver_address = (
            f"{organization.city}, {organization.street}, {organization.building}"
        )

        transfer_time = r.updated_at or r.created_at

        acts.append(WasteTransferActDTO(
            city=organization.city,
            act_date=transfer_time.date(),

            sender_name=client.name,
            sender_edrpou=client.edrpou,
            sender_address=sender_address,
            sender_phone=client.phone_number,

            receiver_name=organization.name,
            receiver_edrpou=organization.edrpou,
            receiver_address=receiver_address,
            receiver_phone=organization.phone_number,

            transfer_datetime=transfer_time,
            waste_description=r.waste_description,
            rejection_reason=None
        ))

    return acts

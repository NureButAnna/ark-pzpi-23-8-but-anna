from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.models import Organization, ContainerSite, Containers
from src.schemas.analytics import ClientCompanyActivityStats, OrganizationActivityStats
from src.database import get_db
from src.models import ClientCompanies, DisposalRequests
from src.api.auth import get_current_user

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics 📊"]
)


@router.get(
    "/client-companies",
    response_model=list[ClientCompanyActivityStats]
)
def client_companies_activity_statistic(
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    _, role = current
    if role != "admin":
        raise HTTPException(403, "Only admin can view analytics")

    statistic = (
        db.query(
            ClientCompanies.client_id,
            ClientCompanies.name,
            func.count(DisposalRequests.request_id).label("total_requests"),
            func.count(
                func.nullif(DisposalRequests.status != "completed", True)
            ).label("completed_requests"),
            func.count(
                func.nullif(DisposalRequests.status == "completed", True)
            ).label("active_requests"),
            func.max(DisposalRequests.created_at).label("last_activity")
        )
        .outerjoin(
            DisposalRequests,
            DisposalRequests.client_id == ClientCompanies.client_id
        )
        .group_by(ClientCompanies.client_id)
        .all()
    )

    return statistic


@router.get(
    "/organizations",
    response_model=list[OrganizationActivityStats]
)
def organizations_activity_statistic(
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    _, role = current
    if role != "admin":
        raise HTTPException(403, "Only admin can view analytics")

    statistic = (
        db.query(
            Organization.organization_id,
            Organization.name,
            func.count(DisposalRequests.request_id).label("total_requests"),
            func.count(
                func.nullif(DisposalRequests.status != "completed", True)
            ).label("completed_requests"),
            func.count(func.distinct(ContainerSite.container_site_id))
                .label("container_sites"),
            func.count(func.distinct(Containers.container_id))
                .label("containers"),
            func.max(DisposalRequests.updated_at).label("last_activity")
        )
        .outerjoin(
            DisposalRequests,
            DisposalRequests.organization_id == Organization.organization_id
        )
        .outerjoin(
            ContainerSite,
            ContainerSite.organization_id == Organization.organization_id
        )
        .outerjoin(
            Containers,
            Containers.container_site_id == ContainerSite.container_site_id
        )
        .group_by(Organization.organization_id)
        .all()
    )

    return statistic

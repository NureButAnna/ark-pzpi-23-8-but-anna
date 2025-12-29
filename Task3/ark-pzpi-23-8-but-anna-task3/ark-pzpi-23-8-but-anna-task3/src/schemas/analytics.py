from pydantic import BaseModel
from datetime import datetime


class ClientCompanyActivityStats(BaseModel):
    client_id: int
    name: str
    total_requests: int
    completed_requests: int
    active_requests: int
    last_activity: datetime | None


class OrganizationActivityStats(BaseModel):
    organization_id: int
    name: str
    total_requests: int
    completed_requests: int
    container_sites: int
    containers: int
    last_activity: datetime | None

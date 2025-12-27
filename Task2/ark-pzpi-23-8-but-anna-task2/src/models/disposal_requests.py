from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database import Base


class DisposalRequests(Base):
    __tablename__ = "disposal_requests"

    request_id = Column(Integer, primary_key=True, index=True)
    waste_type = Column(String(100), nullable=False)
    waste_description = Column(Text)
    amount_kg = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)
    status = Column(String(50))

    organization_id = Column(Integer, ForeignKey(
        "organization.organization_id", ondelete="CASCADE"))
    client_id = Column(Integer, ForeignKey(
        "clientcompanies.client_id", ondelete="CASCADE"))

    organization = relationship(
        "Organization", back_populates="disposal_requests")
    client = relationship(
        "ClientCompanies", back_populates="disposal_requests")

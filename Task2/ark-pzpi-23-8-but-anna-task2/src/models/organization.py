from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.database import Base


class Organization(Base):
    __tablename__ = "organization"

    organization_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    type = Column(String(50))
    city = Column(String(100))
    street = Column(String(100))
    building = Column(String(20))
    phone_number = Column(String(20))
    email = Column(String(150), nullable=False)
    password_hash = Column(String(255), nullable=False)
    edrpou = Column(String(20))

    container_sites = relationship(
        "ContainerSite", back_populates="organization")
    disposal_requests = relationship(
        "DisposalRequests", back_populates="organization")

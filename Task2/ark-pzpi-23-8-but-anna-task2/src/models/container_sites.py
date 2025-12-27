from sqlalchemy import Column, Integer, Float, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from src.database import Base


class ContainerSite(Base):
    __tablename__ = "containersite"

    container_site_id = Column(Integer, primary_key=True, index=True)
    location_lat = Column(String(100), nullable=False)
    location_lng = Column(String(100), nullable=False)
    city = Column(String(100))
    street = Column(String(100))
    building = Column(String(20))
    entrance = Column(String(10))
    description = Column(Text)

    organization_id = Column(Integer, ForeignKey(
        "organization.organization_id", ondelete="CASCADE"))

    organization = relationship(
        "Organization", back_populates="container_sites")
    containers = relationship("Containers", back_populates="site")
    pickups = relationship("Pickups", back_populates="site")
    notifications = relationship(
        "Notifications", back_populates="containersite")

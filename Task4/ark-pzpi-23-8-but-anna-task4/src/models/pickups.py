from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base


class Pickups(Base):
    __tablename__ = "pickups"

    pickup_id = Column(Integer, primary_key=True, index=True)
    scheduled_time = Column(DateTime)
    completed_time = Column(DateTime)

    container_site_id = Column(Integer, ForeignKey(
        "containersite.container_site_id", ondelete="CASCADE"))
    vehicle_id = Column(Integer, ForeignKey(
        "vehicles.vehicle_id", ondelete="SET NULL"))

    site = relationship("ContainerSite", back_populates="pickups")
    vehicle = relationship("Vehicles", back_populates="pickups")

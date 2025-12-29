from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base


class Vehicles(Base):
    __tablename__ = "vehicles"

    vehicle_id = Column(Integer, primary_key=True, index=True)
    vehicle_name = Column(String(100))
    number_plate = Column(String(20), unique=True, nullable=False)

    organization_id = Column(Integer, ForeignKey(
        "containersite.container_site_id", ondelete="CASCADE"))

    pickups = relationship("Pickups", back_populates="vehicle")

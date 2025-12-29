from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database import Base


class Devices(Base):
    __tablename__ = "devices"

    device_id = Column(Integer, primary_key=True, index=True)
    device_name = Column(String(100), nullable=False)
    serial_number = Column(String(100), nullable=False)
    device_type = Column(String(50))
    last_signal = Column(DateTime, default=datetime.utcnow)
    battery_level = Column(Integer)
    status = Column(String(50))

    container_id = Column(Integer, ForeignKey(
        "containers.container_id", ondelete="SET NULL"))

    container = relationship("Containers", back_populates="devices")

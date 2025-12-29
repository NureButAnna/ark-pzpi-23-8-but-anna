from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database import Base


class Containers(Base):
    __tablename__ = "containers"

    container_id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False)
    capacity = Column(Integer)
    fill_level = Column(Integer)
    status = Column(String(50), nullable=False)
    tilted = Column(Boolean, default=False)
    last_update = Column(DateTime, default=datetime.utcnow)

    container_site_id = Column(
        Integer,
        ForeignKey("containersite.container_site_id", ondelete="CASCADE")
    )

    site = relationship("ContainerSite", back_populates="containers")
    devices = relationship("Devices", back_populates="container")

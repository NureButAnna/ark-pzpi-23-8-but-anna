from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database import Base


class Notifications(Base):
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    message_type = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    container_site_id = Column(Integer, ForeignKey(
        "containersite.container_site_id", ondelete="SET NULL"))

    user = relationship("Users", back_populates="notifications")
    containersite = relationship(
        "ContainerSite", back_populates="notifications")

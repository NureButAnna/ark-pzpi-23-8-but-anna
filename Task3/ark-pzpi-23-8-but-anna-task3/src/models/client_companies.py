from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.database import Base


class ClientCompanies(Base):
    __tablename__ = "clientcompanies"

    client_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    type = Column(String(100))
    city = Column(String(100))
    street = Column(String(100))
    building = Column(String(20))
    phone_number = Column(String(20))
    email = Column(String(150), nullable=False)
    password_hash = Column(String(255), nullable=False)
    edrpou = Column(String(20))

    disposal_requests = relationship(
        "DisposalRequests", back_populates="client")

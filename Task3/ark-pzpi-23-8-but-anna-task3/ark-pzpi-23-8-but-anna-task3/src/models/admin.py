from sqlalchemy import Column, Integer, String
from src.database import Base


class Admins(Base):
    __tablename__ = "admins"

    admin_id = Column(Integer, primary_key=True, index=True)
    last_name = Column(String(100), nullable=False)
    first_name = Column(String(100), nullable=False)
    patronymic = Column(String(100))
    password_hash = Column(String(255), nullable=False)
    email = Column(String(150), nullable=False)

# backend/modelos/user.py

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from backend.database.config import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    balance = Column(Float, default=10000.0)  # Balance inicial

    transactions = relationship("Transaction", back_populates="user")
    portfolio = relationship("Portfolio", uselist=False, back_populates="user")

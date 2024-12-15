from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.database.config import Base

# Modelo de Portafolio
class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    btc_amount = Column(Float, default=0.0)
    current_value = Column(Float, default=0.0)

    user = relationship("User")

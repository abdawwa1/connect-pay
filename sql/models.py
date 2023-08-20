# SQL-ALCHEMY MODELS
from sqlalchemy import DECIMAL, Column, Integer, String, JSON
from sqlalchemy.orm import relationship

from .settings import Base


class Payment(Base):
    __tablename__ = "payment"

    id = Column(Integer, primary_key=True, index=True)
    integrator = Column(String, index=True)
    request = Column(JSON)
    response = Column(JSON)
    amount = Column(DECIMAL)

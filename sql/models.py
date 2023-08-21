# SQL-ALCHEMY MODELS
import enum
from sqlalchemy import DECIMAL, Column, Integer, String, JSON, Enum
from .settings import Base


class PaymentStatus(enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Payment(Base):
    __tablename__ = "payment"

    id = Column(Integer, primary_key=True, index=True)
    integrator = Column(String, index=True)
    request = Column(JSON)
    response = Column(JSON)
    amount = Column(DECIMAL)
    status = Column(Enum(PaymentStatus))


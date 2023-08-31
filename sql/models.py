# SQL-ALCHEMY MODELS
import enum
from sqlalchemy import DECIMAL, Column, Integer, String, JSON, Enum, Boolean
from .settings import Base


class PaymentStatus(enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Providers(enum.Enum):
    HyperPay = "HyperPay"
    PayPal = "PayPal"


class Payment(Base):
    __tablename__ = "payment"

    id = Column(Integer, primary_key=True, index=True)
    integrator = Column(String, index=True)
    request = Column(JSON)
    response = Column(JSON)
    amount = Column(DECIMAL)
    status = Column(Enum(PaymentStatus))


class IntegratorConfig(Base):
    __tablename__ = "integrator_config"

    id = Column(Integer, primary_key=True, index=True)
    providers = Column(Enum(Providers), nullable=False)
    enabled = Column(Boolean, default=False, nullable=False)
    config_data = Column(JSON)


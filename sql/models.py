# SQL-ALCHEMY MODELS
import enum
from sqlalchemy import DECIMAL, Column, Integer, String, JSON, Enum, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .settings import Base


class PaymentStatus(enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Providers(enum.Enum):
    HyperPay = "HyperPay"
    PayPal = "PayPal"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    user_name = Column(String, index=True, nullable=False, unique=True)
    external_id = Column(String, nullable=False, unique=True)

    integrator_config = relationship('IntegratorConfig', back_populates="user")
    payment = relationship('Payment', back_populates="user")

    def __str__(self):
        return self.user_name


class Payment(Base):
    __tablename__ = "payment"

    id = Column(Integer, primary_key=True, index=True)
    integrator = Column(String, index=True)
    request = Column(JSON)
    response = Column(JSON)
    amount = Column(DECIMAL)
    status = Column(Enum(PaymentStatus))
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="payment")


class IntegratorConfig(Base):
    __tablename__ = "integrator_config"

    id = Column(Integer, primary_key=True, index=True)
    providers = Column(Enum(Providers), nullable=False)
    enabled = Column(Boolean, default=False, nullable=False)
    config_data = Column(JSON)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="integrator_config")

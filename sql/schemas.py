# PYDANTIC MODELS
"""
These models were created for data validation/annotations.
"""
from enum import Enum
from decimal import Decimal
from pydantic import BaseModel, Json

from sql.models import Providers


class PaymentBase(BaseModel):
    integrator: str


class PaymentEnum(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class PaymentCreate(PaymentBase):
    request: Json
    response: Json
    status: PaymentEnum = PaymentEnum.PENDING
    amount: Decimal
    user_id: int


class PaymentSuccessUpdate(PaymentBase):
    response: Json
    status: PaymentEnum = PaymentEnum.SUCCESS


class UserBase(BaseModel):
    user_name: str


class UserCreate(UserBase):
    external_id: str

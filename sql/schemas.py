# PYDANTIC MODELS
"""
These models were created for data validation/annotations.
"""
from enum import Enum
from decimal import Decimal
from pydantic import BaseModel, Json


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


class PaymentSuccessUpdate(PaymentBase):
    response: Json
    status: PaymentEnum = PaymentEnum.SUCCESS

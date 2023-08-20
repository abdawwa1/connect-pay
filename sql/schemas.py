# PYDANTIC MODELS

from pydantic import BaseModel, Json


class PaymentBase(BaseModel):
    integrator: str


class PaymentCreate(PaymentBase):
    request: Json
    response: Json

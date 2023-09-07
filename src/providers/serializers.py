from sql.models import Providers
from pydantic import BaseModel
from decimal import Decimal


class HyperPaySerializer(BaseModel):
    card_type: str
    amount: Decimal
    currency: str


class PaypalSerializer(BaseModel):
    amount: Decimal
    currency: str


class PaymentData(BaseModel):
    checkout_id: str


class Integrator(BaseModel):
    providers: Providers
    enabled: bool


class IntegratorCreate(Integrator):
    config_data: dict

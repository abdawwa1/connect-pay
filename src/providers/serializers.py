from pydantic import BaseModel
from decimal import Decimal


class HyperPaySerializer(BaseModel):
    card_type: str
    amount: Decimal
    currency: str


class PaypalSerializer(BaseModel):
    amount: Decimal
    currency: str

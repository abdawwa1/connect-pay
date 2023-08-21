from decimal import Decimal
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from src.providers.connect import Connect

from sqladmin import Admin
from sql.models import Payment
from sqladmin import ModelView
from sql.settings import engine

import logging

logger = logging.getLogger("uvicorn")

app = FastAPI()


class ProviderRequest(BaseModel):
    provider_name: str
    card_type: Optional[str] = None
    amount: Decimal
    currency: str


@app.post("/provider/checkout")
async def process_provider(data: ProviderRequest):
    provider = Connect()

    client = None
    if data.provider_name == "HyperPay":
        if not data.card_type:
            raise HTTPException(status_code=400, detail="Card type is required")
        client = provider.get_provider(data.provider_name, data.card_type)
    elif data.provider_name == "PayPal":
        if data.card_type:
            raise HTTPException(status_code=400, detail="Remove Card Type")
        client = provider.get_provider(data.provider_name)

    if not client:
        raise HTTPException(status_code=400, detail="Provider name not found")

    return client.initiate_payment(amount=data.amount, currency=data.currency)


class PaymentData(BaseModel):
    checkout_id: str


@app.get("/{provider}/payment/status")
async def payment_result(provider: str, data: PaymentData):
    client = None
    if provider == "HyperPay":
        client = Connect().get_provider(provider, "ignore")  # Todo: Ignore is just temporary for logic fix
    elif provider == "PayPal":
        client = Connect().get_provider(provider)

    if not client:
        raise HTTPException(status_code=400, detail="Provider name not found")

    return client.get_payment_status(data.checkout_id)


"""
Add Models for admin panel below
"""
admin = Admin(app, engine)


class PaymentAdmin(ModelView, model=Payment):
    column_list = [Payment.id, Payment.integrator, Payment.status]
    column_sortable_list = [Payment.id, Payment.integrator, Payment.status]


admin.add_view(PaymentAdmin)

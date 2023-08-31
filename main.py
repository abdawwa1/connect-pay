from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from sql.hyperpay_crud import hyperpay_config
from sql.paypal_crud import paypal_config
from src.providers.connect import Connect

from sqladmin import Admin
from sql.models import Payment, IntegratorConfig
from sqladmin import ModelView
from sql.settings import engine, SessionLocal

import logging

from src.providers.serializers import HyperPaySerializer, PaypalSerializer

logger = logging.getLogger("uvicorn")

app = FastAPI()


@app.post("/{integrator}/checkout")
async def process_provider(integrator: str, request: Request):
    provider = Connect()
    data = await request.json()

    client = None
    if integrator == "HyperPay":
        if not hyperpay_config(SessionLocal()):
            raise HTTPException(status_code=400, detail="No configurations were added please check portal!")
        try:
            serializer = HyperPaySerializer(**data)
        except Exception:
            raise HTTPException(status_code=400)

        if not hyperpay_config(SessionLocal()).enabled:
            raise HTTPException(status_code=400, detail="Provider not enabled please check portal!")

        client = provider.get_provider(integrator, serializer.card_type)

    elif integrator == "PayPal":
        if not paypal_config(SessionLocal()):
            raise HTTPException(status_code=400, detail="No configurations were added please check portal!")
        try:
            PaypalSerializer(**data)
        except Exception:
            raise HTTPException(status_code=400)

        if not paypal_config(SessionLocal()).enabled:
            raise HTTPException(status_code=400, detail="Provider not enabled please check portal!")
        client = provider.get_provider(integrator)

    if not client:
        raise HTTPException(status_code=400, detail="Provider name not found")

    return client.initiate_payment(amount=data.get("amount"), currency=data.get("currency"))


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
    icon = "fa fa-bars"


class IntegratorConfigAdmin(ModelView, model=IntegratorConfig):
    column_list = [IntegratorConfig.id, IntegratorConfig.providers, IntegratorConfig.enabled]
    column_sortable_list = [IntegratorConfig.id, IntegratorConfig.providers, IntegratorConfig.enabled]
    icon = "fa fa-plus-circle"
    create_template = "integrator_create.html"
    edit_template = "integrator_edit.html"


admin.add_view(PaymentAdmin)
admin.add_view(IntegratorConfigAdmin)

from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.providers.connect import Connect
import logging

logger = logging.getLogger("uvicorn")

app = FastAPI()


class ProviderRequest(BaseModel):
    provider_name: str
    card_type: Optional[str] = None


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

    return client.initiate_payment()


class PaymentData(BaseModel):
    checkout_id: str


@app.get("/{provider}/payment/status")
async def payment_result(provider: str, data: PaymentData):
    client = None
    if provider == "HyperPay":
        client = Connect().get_provider(provider)
    elif provider == "PayPal":
        client = Connect().get_provider(provider)

    if not client:
        raise HTTPException(status_code=400, detail="Provider name not found")

    return client.get_payment_status(data.checkout_id)

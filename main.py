from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from src.providers.connect import Connect
import logging

logger = logging.getLogger("uvicorn")

app = FastAPI()


class ProviderRequest(BaseModel):
    provider_name: str
    card_type: Optional[str]


@app.post("/provider/")
async def process_provider(data: ProviderRequest):
    if data.provider_name == "HyperPay":
        client = Connect().get_provider(data.provider_name, data.card_type)
        return client.initiate_payment()


class PaymentData(BaseModel):
    checkout_id: str


@app.get("/{provider}/payment/status")
async def payment_result(provider: str, data: PaymentData):
    if provider == "HyperPay":
        client = Connect().get_provider(provider)
        return client.get_payment_status(data.checkout_id)

from fastapi import FastAPI
from src.providers.connect import Connect

app = FastAPI()


@app.get("/provider/{provider_name}")
async def get_provider(provider_name: str):
    provider = Connect()
    client = provider.get_provider(provider_name)
    return client.initiate_payment()

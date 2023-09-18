from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware

from sql.orms import integrator_crud, payment_crud
from sql.orms.hyperpay_crud import hyperpay_config
from sql.orms.paypal_crud import paypal_config
from sql.users_crud import get_user
from src.middlewares import KCTokenBackend
from src.providers.connect import Connect
from config import get_settings
from sql.settings import SessionLocal

import logging

from src.providers.serializers import HyperPaySerializer, PaypalSerializer, IntegratorCreate

logger = logging.getLogger("uvicorn")
settings = get_settings()

realm_secret = settings.get("connect_pay_key").replace("\\n", "\n")
auth_backend = KCTokenBackend(
    realm_secret,
    options={
        'verify_aud': False
    }
)
middleware = [
    Middleware(AuthenticationMiddleware, backend=auth_backend)
]
app = FastAPI(middleware=middleware, debug=True)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/integrator/", status_code=200)
async def get_integrator(request: Request):
    return integrator_crud.get_integrators(SessionLocal(), request.user.id)


@app.get("/payments/", status_code=200)
async def get_payments(request: Request):
    return payment_crud.get_user_payments(SessionLocal(), request.user.id)


@app.post("/integrator/create", status_code=201)
async def create_integrator(integrator: IntegratorCreate, request: Request):
    db_session = SessionLocal()
    user = get_user(db_session, request.user.external_id)
    integrator_record = integrator_crud.get_integrator(db_session, integrator.providers.value, user.id)

    if integrator_record:
        raise HTTPException(status_code=400, detail="Config exists")
    else:
        integrator_crud.create_integrator(
            db_session,
            IntegratorCreate(
                providers=integrator.providers.value,
                enabled=integrator.enabled,
                config_data=integrator.config_data,
            ),
            user_id=user.id
        )
        return JSONResponse(
            content={
                "message": "Successfully created config!"
            }
        )


@app.put("/integrator/update/{pk}", status_code=200)
async def update_integrator(integrator: IntegratorCreate, pk: int, request: Request):
    db_session = SessionLocal()
    user = get_user(db_session, request.user.external_id)
    integrator_record = integrator_crud.get_integrator_by_id(db_session, pk, user.id)

    if not integrator_record:
        raise HTTPException(status_code=400, detail="Config not found !")
    else:
        integrator_crud.update_integrator(
            db_session,
            pk,
            IntegratorCreate(
                providers=integrator.providers.value,
                enabled=integrator.enabled,
                config_data=integrator.config_data,
            ),
        )
        return JSONResponse(
            content={
                "message": "Successfully updated config!"
            }
        )


@app.delete("/integrator/delete/{pk}", status_code=200)
async def delete_integrator(pk: int, request: Request):
    db_session = SessionLocal()
    user = get_user(db_session, request.user.external_id)
    integrator_record = integrator_crud.get_integrator_by_id(db_session, pk, user.id)

    if not integrator_record:
        raise HTTPException(status_code=400, detail="Config not found !")
    else:
        integrator_crud.delete_integrator(
            db_session,
            pk,
            user.id
        )
        return JSONResponse(
            content={
                "message": "Successfully deleted config!"
            }
        )


@app.post("/{integrator}/checkout")
async def process_provider(integrator: str, request: Request):
    provider = Connect()
    data = await request.json()

    client = None
    if integrator == "hyperpay":
        hyperpay_settings = hyperpay_config(SessionLocal(), request.user.id)
        if not hyperpay_settings:
            raise HTTPException(status_code=400, detail="No configurations were added please check portal!")
        try:
            serializer = HyperPaySerializer(**data)
        except Exception:
            raise HTTPException(status_code=400)

        if not hyperpay_settings.enabled:
            raise HTTPException(status_code=400, detail="Provider not enabled please check portal!")
        client = provider.get_provider(integrator, serializer.card_type, config_data=hyperpay_settings.config_data,
                                       user_id=hyperpay_settings.user_id)

    elif integrator == "paypal":
        paypal_settings = paypal_config(SessionLocal(), request.user.id)

        if not paypal_settings:
            raise HTTPException(status_code=400, detail="No configurations were added please check portal!")
        try:
            PaypalSerializer(**data)
        except Exception:
            raise HTTPException(status_code=400)

        if not paypal_settings.enabled:
            raise HTTPException(status_code=400, detail="Provider not enabled please check portal!")

        client = provider.get_provider(integrator, config_data=paypal_settings.config_data,
                                       user_id=paypal_settings.user_id)

    if not client:
        raise HTTPException(status_code=400, detail="Provider name not found")

    return client.initiate_payment(amount=data.get("amount"), currency=data.get("currency"))


@app.get("/{provider}/payment/status/{checkout_id}")
async def payment_result(provider: str, checkout_id: str, request: Request):
    client = None
    if provider == "hyperpay":
        hyperpay_settings = hyperpay_config(SessionLocal(), request.user.id)
        if not hyperpay_settings:
            raise HTTPException(status_code=400, detail="No configurations were added please check portal!")

        if not hyperpay_settings.enabled:
            raise HTTPException(status_code=400, detail="Provider not enabled please check portal!")

        client = Connect().get_provider(provider, "ignore",
                                        config_data=hyperpay_settings.config_data)  # Todo: Ignore is just temporary for logic fix
    elif provider == "paypal":
        paypal_settings = paypal_config(SessionLocal(), request.user.id)

        if not paypal_settings:
            raise HTTPException(status_code=400, detail="No configurations were added please check portal!")

        if not paypal_settings.enabled:
            raise HTTPException(status_code=400, detail="Provider not enabled please check portal!")

        client = Connect().get_provider(provider, config_data=paypal_settings.config_data)

    if not client:
        raise HTTPException(status_code=400, detail="Provider name not found")

    return client.get_payment_status(checkout_id)

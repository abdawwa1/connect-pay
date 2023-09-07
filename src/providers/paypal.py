import json
import logging
import requests
from fastapi import HTTPException

from config import get_settings
from sql.models import PaymentStatus
from sql.paypal_crud import create_payment, update_payment, paypal_config
from sql.schemas import PaymentCreate, PaymentSuccessUpdate
from sql.settings import SessionLocal
from src.providers.base import BaseProvider

logger = logging.getLogger("uvicorn")
settings = get_settings()


class PayPal(BaseProvider):
    DEFAULT_CURRENCY = "USD"
    db = SessionLocal()

    def __init__(self, integrator):
        self.integrator_data = integrator
        self.base_url = integrator.get("config_data").get("paypal-base-url")
        self.access_token = self.get_access_token()
        self.data = {}
        self.response_data = {}

    def initiate_payment(self, amount, currency):
        checkout_url = self.base_url + "/v2/checkout/orders"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.authentication_headers,
        }

        self.data = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": "USD",
                        "value": "100.00"
                    }
                }
            ],
            "payment_source": {
                "paypal": {
                    "experience_context": {
                        "payment_method_preference": "UNRESTRICTED",
                        "payment_method_selected": "PAYPAL",
                        "brand_name": "EXAMPLE INC",
                        "locale": "en-US",
                        "landing_page": "LOGIN",
                        "shipping_preference": "NO_SHIPPING",
                        "user_action": "PAY_NOW",
                        "return_url": "https://example.com/returnUrl",
                        "cancel_url": "https://example.com/cancelUrl"
                    }
                }
            }
        }
        try:
            logger.info("******************************************")
            logger.info("initiate-payment-request: {}".format(self.data))
            self.response_data = requests.post(checkout_url, headers=headers, data=json.dumps(self.data)).json()
            self.create_payment_in_db()
            logger.info("******************************************")
            logger.info("paypal-response: {}".format(self.response_data))
        except requests.exceptions.RequestException as error:
            raise HTTPException(status_code=500, detail=error)

        if "PAYER_ACTION_REQUIRED" in self.response_data:
            response = {
                "id": self.response_data["id"],
                "status": self.response_data["status"],
                "links": self.response_data["links"][1]
            }
            return response

        return self.response_data

    def get_payment_status(self, payment_id: str):
        url = self.base_url + f"/v2/checkout/orders/{payment_id}"

        headers = {
            'Authorization': self.authentication_headers,
        }
        self.response_data = requests.get(url, headers=headers).json()

        if "status" in self.response_data and self.response_data.get("status") == "APPROVED":
            self.response_data = self.capture_payment(payment_id)
            self.update_payment_in_db(payment_id)

        return self.response_data

    def auth_paypal(self, client_id, client_secret):
        from requests.auth import HTTPBasicAuth
        from fastapi.exceptions import HTTPException

        auth_url = f"{self.base_url}/v1/oauth2/token"
        payload = {"grant_type": "client_credentials"}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        try:
            response_data = requests.post(
                auth_url, payload, auth=HTTPBasicAuth(client_id, client_secret), headers=headers
            ).json()
        except requests.exceptions.RequestException as error:
            raise HTTPException(status_code=500, detail=error)

        if "access_token" in response_data:
            return response_data["access_token"]

        raise HTTPException(status_code=400, detail=response_data)

    def get_access_token(self):
        return self.auth_paypal(self.integrator_data.get("config_data").get("paypal-client-id"),
                                self.integrator_data.get("config_data").get("paypal-client-secret"))

    def capture_payment(self, payment_id):
        url = self.base_url + f"/v2/checkout/orders/{payment_id}/capture"

        headers = {
            'Authorization': self.authentication_headers,
            'Content-Type': 'application/json'
        }

        request = {
            "headers": headers,
            "url": url
        }

        logger.info("capturing-payment: {}".format(request))
        response = requests.post(url, headers=headers).json()
        return response

    @property
    def authentication_headers(self):
        """
        Return the authentication headers.
        """
        return "Bearer {}".format(self.access_token)

    def create_payment_in_db(self):
        from decimal import Decimal
        return create_payment(
            self.db,
            PaymentCreate(
                integrator="PayPal",
                request=json.dumps(self.data, default=str),
                response=json.dumps(self.response_data, default=str),
                status=PaymentStatus.PENDING.value,
                amount=Decimal(self.data.get("purchase_units")[0].get("amount").get("value"))
            )
        )

    def update_payment_in_db(self, payment_id):
        update_payment(
            self.db,
            payment_id,
            PaymentSuccessUpdate(
                integrator="PayPal",
                response=json.dumps(self.response_data, default=str),
                status=PaymentStatus.SUCCESS.value
            )
        )

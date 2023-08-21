import json
import logging
import requests
from fastapi import HTTPException

from config import get_settings
from src.providers.base import BaseProvider

logger = logging.getLogger("uvicorn")
settings = get_settings()


class PayPal(BaseProvider):
    DEFAULT_CURRENCY = "USD"

    def __init__(self):
        self.base_url = settings.get("paypal_base_url")
        self.access_token = self.get_access_token()

    def initiate_payment(self, amount, currency):
        checkout_url = self.base_url + "/v2/checkout/orders"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.authentication_headers,
        }

        data = {
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
            response_data = requests.post(checkout_url, headers=headers, data=json.dumps(data)).json()
        except requests.exceptions.RequestException as error:
            raise HTTPException(status_code=500, detail=error)

        if "PAYER_ACTION_REQUIRED" in response_data:
            response = {
                "id": response_data["id"],
                "status": response_data["status"],
                "links": response_data["links"][1]
            }
            return response

        return response_data

    def get_payment_status(self, payment_id: str):
        url = self.base_url + f"/v2/checkout/orders/{payment_id}"

        headers = {
            'Authorization': self.authentication_headers,
        }
        response = requests.get(url, headers=headers).json()
        if "status" in response and response.get("status") == "APPROVED":
            response = self.capture_payment(payment_id)

        return response

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
        return self.auth_paypal(settings.get("paypal_client_id"), settings.get("paypal_client_secret"))

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

from src.providers.base import BaseProvider
from config import get_settings
import json
import requests

settings = get_settings()


class HyperPay(BaseProvider):
    DEFAULT_PAYMENT_TYPE = "DB"
    DEFAULT_CURRENCY = "SAR"
    CHECKOUTS_ENDPOINT = "/v1/checkouts"
    RESULT_CODE_SUCCESSFULLY_CREATED_CHECKOUT = "000.200.100"

    def __init__(self):
        self.base_url = settings.get("base_url")
        self.access_token = settings.get("access_token")
        self.entity_id = settings.get("visa_entity_id")
        self.request_log = {}
        self.response_log = {}

    def initiate_payment(self):
        checkouts_api_url = self.base_url + self.CHECKOUTS_ENDPOINT
        payload = {
            "entityId": self.entity_id,
            "amount": "500",
            "currency": self.DEFAULT_CURRENCY,
            "paymentType": self.DEFAULT_PAYMENT_TYPE
        }
        response_data = requests.post(
            checkouts_api_url, payload, headers=self.authentication_headers
        ).json()

        return response_data

    def verify_payment(self):
        pass

    @property
    def authentication_headers(self):
        """
        Return the authentication headers.
        """
        return {"Authorization": "Bearer {}".format(self.access_token)}

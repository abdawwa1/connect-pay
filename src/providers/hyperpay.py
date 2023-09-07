import json

from src.providers.base import BaseProvider
from config import get_settings
import requests
import logging
from src.providers.exceptions import HyperpayException
from fastapi import HTTPException, Depends
from sql.hyperpay_crud import create_payment, get_payment, update_payment, hyperpay_config
from sql.schemas import PaymentCreate, PaymentSuccessUpdate
from sql.models import PaymentStatus
from sql.settings import SessionLocal

logger = logging.getLogger("uvicorn")

settings = get_settings()


class HyperPay(BaseProvider):
    DEFAULT_PAYMENT_TYPE = "DB"
    DEFAULT_CURRENCY = "USD"
    CHECKOUTS_ENDPOINT = "/v1/checkouts"
    RESULT_CODE_SUCCESSFULLY_CREATED_CHECKOUT = "000.200.100"
    db = SessionLocal()

    def __init__(self, integrator, card_type=None):

        self.config_data = integrator.get("config_data")
        self.base_url = self.config_data.get("hyper-pay-base-url")
        self.access_token = self.config_data.get("hyper-pay-token")
        self.entity_id = self.config_data.get(f"hyper-pay-{self.validate_card_type(card_type)}-entity-id")
        self.request_log = {}
        self.response_log = {}

    def initiate_payment(self, amount, currency):
        checkouts_api_url = self.base_url + self.CHECKOUTS_ENDPOINT
        payload = {
            "entityId": self.entity_id,
            "amount": amount,
            "currency": currency,
            "paymentType": self.DEFAULT_PAYMENT_TYPE
        }
        try:
            self.request_log = {
                "method": "POST",
                "url": checkouts_api_url,
                "headers": self.authentication_headers,
                "data": payload,
            }
            logger.info("******************************************")
            logger.info("initiate-payment-request: {}".format(self.request_log))
            response_data = requests.post(
                checkouts_api_url, payload, headers=self.authentication_headers
            ).json()
            self.response_log = response_data
            logger.info("******************************************")
            logger.info("hyperpay-response: {}".format(self.response_log))
            self.create_payment_in_db()
        except requests.exceptions.RequestException as error:
            raise HyperpayException("Error creating a checkout {}".format(error))

        if "result" not in response_data or "code" not in response_data["result"]:
            raise HyperpayException(
                "Error creating checkout. Invalid response_data from HyperPay."
            )

        result_code = response_data["result"]["code"]

        if result_code != self.RESULT_CODE_SUCCESSFULLY_CREATED_CHECKOUT:
            raise HyperpayException(
                "Error creating checkout. HyperPay status code: %s" % result_code
            )

        return response_data["id"]

    def get_payment_status(self, payment_id):
        import re
        SUCCESS_CODES_REGEX = re.compile(r"^(000\.000\.|000\.100\.1|000\.[36])")
        resource_path = "/v1/checkouts/{}/payment".format(payment_id)
        from urllib.parse import urlencode
        payment_status_api_url = "{}?{}".format(
            self.base_url + resource_path, urlencode({"entityId": self.get_entity_id(payment_id)})
        )

        # log the request
        self.request_log = {
            "method": "GET",
            "url": payment_status_api_url,
            "headers": self.authentication_headers,
            "data": {},
        }
        logger.info("******************************************")
        logger.info("payment-status-request: {}".format(self.request_log))
        try:
            response_data = requests.get(
                payment_status_api_url, headers=self.authentication_headers
            ).json()
            self.response_log = response_data
            logger.info("******************************************")
            logger.info("hyperpay-response: {}".format(self.response_log))

        except requests.exceptions.RequestException as error:
            raise HyperpayException(
                "Received a non-success response from HyperPay %s" % error
            )

        # log the gateway response
        self.response_log = response_data

        result_code = response_data["result"]["code"]

        if SUCCESS_CODES_REGEX.search(result_code):
            self.update_payment_in_db(payment_id)

        return response_data

    def get_entity_id(self, checkout_id):
        payment = get_payment(
            self.db,
            checkout_id
        )
        if not payment:
            raise HyperpayException("Payment Not found")
        else:
            return payment

    def validate_card_type(self, card_type):
        card_type_value, = card_type

        card_types = self.config_data.get("card_type")
        if card_type_value == "ignore":
            return card_type_value
        if card_type_value in card_types and self.config_data.get(f"hyper-pay-{card_type_value}-entity-id"):
            return card_type_value
        else:
            raise HTTPException(status_code=400,
                                detail=f"Invalid card type! Make sure you enabled {card_type_value} & added Entity id")

    @property
    def authentication_headers(self):
        """
        Return the authentication headers.
        """
        return {"Authorization": "Bearer {}".format(self.access_token)}

    def create_payment_in_db(self):
        from decimal import Decimal
        return create_payment(
            self.db,
            PaymentCreate(
                integrator="HyperPay",
                request=json.dumps(self.request_log, default=str),
                response=json.dumps(self.response_log, default=str),
                status=PaymentStatus.PENDING.value,
                amount=Decimal(self.request_log.get("data").get("amount"))
            )
        )

    def update_payment_in_db(self, checkout_id):
        return update_payment(
            self.db,
            checkout_id,
            PaymentSuccessUpdate(
                integrator="HyperPay",
                response=json.dumps(self.response_log, default=str),
                status=PaymentStatus.SUCCESS.value
            )
        )

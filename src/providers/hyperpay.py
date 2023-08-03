from src.providers.base import BaseProvider
from config import get_settings
import requests
import logging
from src.providers.exceptions import HyperpayException
from fastapi import HTTPException

logger = logging.getLogger("uvicorn")

settings = get_settings()


class HyperPay(BaseProvider):
    DEFAULT_PAYMENT_TYPE = "DB"
    DEFAULT_CURRENCY = "SAR"
    CHECKOUTS_ENDPOINT = "/v1/checkouts"
    RESULT_CODE_SUCCESSFULLY_CREATED_CHECKOUT = "000.200.100"

    def __init__(self, card_type=None):
        self.base_url = settings.get("hyperpay_base_url")
        self.access_token = settings.get("access_token")
        self.entity_id = settings.get(f"{self.validate_card_type(card_type)}_entity_id")
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
        resource_path = "/v1/checkouts/{}/payment".format(payment_id)
        from urllib.parse import urlencode
        payment_status_api_url = "{}?{}".format(
            self.base_url + resource_path, urlencode({"entityId": self.get_entity_id(payment_id)})
        )
        logger.info(self.entity_id)
        logger.info(payment_status_api_url)

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

        return response_data

    def get_entity_id(self, checkout_id):
        # TODO: Get entity id from DB based on checkout_id
        return "8a8294174b7ecb28014b9699220015ca"

    def validate_card_type(self, card_type):
        card_types = str(settings.get("card_types")).split(",")
        if card_type not in card_types:
            raise HTTPException(status_code=400, detail="Invalid card type")
        else:
            return card_type

    @property
    def authentication_headers(self):
        """
        Return the authentication headers.
        """
        return {"Authorization": "Bearer {}".format(self.access_token)}

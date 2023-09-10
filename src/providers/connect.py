import logging
from src.providers.hyperpay import HyperPay
from src.providers.paypal import PayPal
from src.providers.base import BaseProvider

logger = logging.getLogger("uvicorn")


class Connect:

    @staticmethod
    def get_provider(provider="dummy", *args, **kwargs) -> BaseProvider:
        if provider == "hyperpay":
            return HyperPay(card_type=args, integrator=kwargs)
        elif provider == "paypal":
            return PayPal(kwargs)

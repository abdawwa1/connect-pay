import logging
from src.providers.hyperpay import HyperPay
from src.providers.base import BaseProvider

logger = logging.getLogger("uvicorn")


class Connect:
    @staticmethod
    def get_provider(provider="dummy", *args, **kwargs) -> BaseProvider:
        providers = {
            "HyperPay": HyperPay(*args)
        }
        return providers[provider]

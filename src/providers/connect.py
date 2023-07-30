from src.providers.hyperpay import HyperPay
from src.providers.base import BaseProvider


class Connect:
    @staticmethod
    def get_provider(provider="dummy", *args, **kwargs) -> BaseProvider:
        providers = {
            "HyperPay": HyperPay
        }
        return providers[provider](*args, **kwargs)

from abc import ABC, abstractmethod
from decimal import Decimal


class BaseProvider(ABC):

    @abstractmethod
    def initiate_payment(self, amount: Decimal, currency: str):
        pass

    @abstractmethod
    def get_payment_status(self, payment_id: str):
        pass

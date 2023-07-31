from abc import ABC, abstractmethod


class BaseProvider(ABC):

    @abstractmethod
    def initiate_payment(self):
        pass

    @abstractmethod
    def get_payment_status(self, payment_id: str):
        pass

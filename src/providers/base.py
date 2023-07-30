from abc import ABC, abstractmethod


class BaseProvider(ABC):

    @abstractmethod
    def initiate_payment(self):
        pass

    @abstractmethod
    def verify_payment(self):
        pass

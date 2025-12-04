
from abc import ABC, abstractmethod

class PromoCatalogPort(ABC):
    @abstractmethod
    def get_applicable_promo(self, product_dto, user_dto):
        pass

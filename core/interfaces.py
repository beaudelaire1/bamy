from __future__ import annotations

from decimal import Decimal
from typing import Iterable, Optional, Protocol

# The domain now provides canonical DTOs in ``core.domain.dto``.
from core.domain.dto import (
    ProductDTO,
    CartItemDTO,
    CartDTO,
    OrderDTO,
    UserDTO,
)


class ProductRepository(Protocol):
    def get_by_id(self, product_id: int) -> ProductDTO: ...
    def get_by_sku(self, sku: str) -> ProductDTO: ...
    def search(self, query: str | None = None) -> Iterable[ProductDTO]: ...


class CartRepository(Protocol):
    def get_for_request(self, request) -> CartDTO: ...
    def save_for_request(self, request, cart: CartDTO) -> CartDTO: ...


class OrderRepository(Protocol):
    def create_from_cart(self, cart: CartDTO, user_id: int | None) -> OrderDTO: ...
    def list_for_user(self, user_id: int) -> Iterable[OrderDTO]: ...
    def get_for_user(self, order_id: int, user_id: int) -> OrderDTO: ...


class PricingService(Protocol):
    """
    Interface de service de tarification.

    - ``get_unit_price`` est la méthode principale, utilisée par les
      couches orientées domaine (Django ORM + moteur de pricing).
    - ``compute_unit_price`` reste disponible pour compatibilité avec
      l'ancien code basé sur ``ProductDTO`` minimal.
    """

    def get_unit_price(self, product: ProductDTO, user: Optional[UserDTO] = None) -> Decimal: ...
    def compute_unit_price(self, product: ProductDTO, client_type: Optional[str] = None) -> Decimal: ...
    def calculate_cart(self, items: Iterable[CartItemDTO], user: Optional[UserDTO] = None): ...

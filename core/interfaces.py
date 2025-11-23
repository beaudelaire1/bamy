from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, Protocol


@dataclass
class ProductDTO:
    id: int
    sku: str
    title: str
    unit_price: Decimal
    is_active: bool


@dataclass
class CartItemDTO:
    product_id: int
    sku: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal


@dataclass
class CartDTO:
    user_id: int | None
    items: list[CartItemDTO]
    total: Decimal


@dataclass
class OrderDTO:
    id: int
    order_number: str
    user_id: int | None
    total: Decimal
    status: str


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
    def compute_unit_price(self, product: ProductDTO, client_type: str | None = None) -> Decimal: ...

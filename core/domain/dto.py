from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class ProductDTO(BaseModel):
    id: int
    sku: str
    price: Decimal
    discount_price: Optional[Decimal] = None
    price_wholesaler: Optional[Decimal] = None
    price_big_retail: Optional[Decimal] = None
    price_small_retail: Optional[Decimal] = None


class UserDTO(BaseModel):
    id: int
    email: str
    client_type: Optional[str] = None
    customer_number: Optional[str] = None
    is_b2b_verified: bool = False


class PromoItemDTO(BaseModel):
    promo_price: Decimal

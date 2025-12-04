
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass(frozen=True)
class ProductDTO:
    id: int
    sku: str
    price: Decimal
    price_wholesaler: Optional[Decimal] = None
    price_big_retail: Optional[Decimal] = None

@dataclass(frozen=True)
class UserDTO:
    id: int
    email: str
    client_type: str
    is_verified: bool

@dataclass(frozen=True)
class PromoItemDTO:
    promo_price: Decimal

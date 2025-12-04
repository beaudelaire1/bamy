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


class ClientDTO(BaseModel):
    """Représente une organisation cliente dans le moteur.

    Le ``ClientDTO`` permet de transmettre des paramètres
    organisationnels depuis les couches supérieures vers les services
    métier.  Il centralise les propriétés du modèle ``Client`` qui
    influencent le pricing et l'accès aux fonctionnalités.
    """

    id: int
    name: str
    settings_currency: Optional[str] = None
    default_pricing_mode: Optional[str] = None
    allowed_features: list[str] | None = None
    sales_rep_id: Optional[int] = None


class PromoItemDTO(BaseModel):
    promo_price: Decimal

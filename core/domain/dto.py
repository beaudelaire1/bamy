"""
Data transfer objects (DTO) used throughout the core domain.

Historically the project defined a number of dataclasses in
``core.interfaces`` to exchange data between the infrastructure layer
and the domain layer.  Mixing multiple DTO definitions led to subtle
inconsistencies and duplicated logic.  To simplify the model and
enforce a single source of truth, all domain-facing DTOs are now
centralised in this module and implemented as `pydantic.BaseModel`
instances.  Using pydantic provides validation and type coercion
without coupling the DTOs to Django or any other framework.  Every
service and repository should import the DTOs from this module rather
than defining ad‑hoc dataclasses.

The ``ProductDTO`` now contains a superset of fields used across the
application (identifier, pricing data and basic merchandising
attributes).  Optional fields allow repositories to populate only the
values they know about (e.g. a catalogue adapter may not provide
``title`` or ``unit_price``).  Additional DTOs have been added for
cart and order data, and these will be used as the canonical types
throughout the refactored codebase.
"""

from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class ProductDTO(BaseModel):
    """DTO representing a product in the pricing engine.

    Attributes beyond the identifier and pricing details are defined as
    optional to allow repositories to supply as much or as little
    information as they have access to.  The ``unit_price`` field is
    provided for backwards compatibility with legacy components; it is
    expected to hold the price that should be charged to the user after
    promotions and B2B rules have been applied.
    """

    id: int
    sku: str
    # Base public price for the product
    price: Decimal
    # Simple discount price set directly on the product (optional)
    discount_price: Optional[Decimal] = None
    # B2B price grid values (optional)
    price_wholesaler: Optional[Decimal] = None
    price_big_retail: Optional[Decimal] = None
    price_small_retail: Optional[Decimal] = None
    # Additional merchandising attributes
    title: Optional[str] = None
    is_active: Optional[bool] = None
    # ``unit_price`` is the final price that should be charged to the
    # customer.  It is left unset by repositories and will be
    # calculated by the pricing service.  Services should update this
    # field when returning priced DTOs.
    unit_price: Optional[Decimal] = None


class UserDTO(BaseModel):
    """DTO representing a user for pricing purposes."""

    id: int
    email: str
    client_type: Optional[str] = None
    customer_number: Optional[str] = None
    is_b2b_verified: bool = False
    # Pricing mode can be provided by higher layers to influence B2B
    # rules (e.g. ``wholesaler``, ``big_retail``, ``small_retail``).  It is
    # optional and will default to the user's client_type when not
    # provided.
    pricing_mode: Optional[str] = None


class ClientDTO(BaseModel):
    """Represents an organisational client in the pricing engine."""

    id: int
    name: str
    settings_currency: Optional[str] = None
    default_pricing_mode: Optional[str] = None
    allowed_features: Optional[List[str]] = None
    sales_rep_id: Optional[int] = None


class PromoItemDTO(BaseModel):
    """DTO representing a catalog promotion item."""

    promo_price: Decimal


class CartItemDTO(BaseModel):
    """DTO representing a single line item in a cart.

    ``product`` holds a ``ProductDTO``.  It is expected that the
    pricing service will populate ``unit_price`` and ``total_price``
    fields during cart calculation.
    """

    product: ProductDTO
    quantity: int
    # Pricing fields.  They are optional before pricing has been
    # calculated.  After running through the pricing service these
    # values will be set on each cart item.
    unit_price: Optional[Decimal] = None
    total_price: Optional[Decimal] = None


class CartDTO(BaseModel):
    """DTO representing a customer's cart."""

    user_id: Optional[int]
    items: List[CartItemDTO] = Field(default_factory=list)
    total: Optional[Decimal] = None


class OrderDTO(BaseModel):
    """DTO representing a persisted order."""

    id: int
    order_number: str
    user_id: Optional[int]
    total: Decimal
    status: str


class CartPricingResult(BaseModel):
    """Result returned by the pricing service when pricing a cart.

    The pricing service will return both the priced list of items and
    the total amount.  This DTO is used internally by services to
    separate the concerns of session management from pricing.
    """

    items: List[CartItemDTO]
    total: Decimal
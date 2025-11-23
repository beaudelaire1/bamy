"""
Fabrique centralisée pour instancier les services du domaine.

Ce module permet de sélectionner les implémentations concrètes des
repositories (base locale Django, futur ERP, etc.) sans coupler les
vues HTTP à ces détails d'infrastructure.
"""

from __future__ import annotations

from django.conf import settings

from core.repositories.products_django import DjangoProductRepository
from core.repositories.cart_session import SessionCartRepository
from core.repositories.orders_django import DjangoOrderRepository
from core.repositories.pricing_simple import SimplePricingService
from core.services.cart import CartService
from core.services.orders import OrderService
from core.services.products import ProductService


def get_product_service() -> ProductService:
    repo = DjangoProductRepository()
    return ProductService(product_repo=repo)


def get_cart_service() -> CartService:
    product_repo = DjangoProductRepository()
    cart_repo = SessionCartRepository()
    pricing_service = SimplePricingService()
    return CartService(
        product_repo=product_repo,
        cart_repo=cart_repo,
        pricing_service=pricing_service,
    )


def get_order_service() -> OrderService:
    cart_repo = SessionCartRepository()
    order_repo = DjangoOrderRepository()
    return OrderService(cart_repo=cart_repo, order_repo=order_repo)

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from core.domain.dto import ProductDTO, UserDTO
from core.domain.pricing_engine import PricingEngine
from core.ports.promo_catalog_port import PromoCatalogPort


class PromoAwareB2BPricingService:
    """Service de pricing centralisé.

    Cette implémentation applique :

    1. Les promotions de catalogue ciblées par numéro client.
    2. La grille tarifaire B2B (wholesaler / big_retail / small_retail)
       avec surcharge +5% pour les comptes non vérifiés.
    3. La promotion simple ``discount_price``.
    4. Le prix public ``price`` en dernier recours.
    """

    def __init__(self, promo_catalog_adapter: PromoCatalogPort) -> None:
        self.promo_port = promo_catalog_adapter

    # API principale utilisée par le reste du système
    def get_unit_price(self, product, user=None) -> Decimal:
        """Calcule le prix unitaire final pour un produit et un utilisateur donnés.

        ``product`` et ``user`` sont ici les objets Django ORM.
        """
        product_dto = ProductDTO(
            id=product.id,
            sku=getattr(product, "article_code", "") or getattr(product, "sku", ""),
            price=product.price,
            discount_price=getattr(product, "discount_price", None),
            price_wholesaler=getattr(product, "price_wholesaler", None),
            price_big_retail=getattr(product, "price_big_retail", None),
            price_small_retail=getattr(product, "price_small_retail", None),
        )

        user_dto: Optional[UserDTO] = None
        if user is not None and getattr(user, "is_authenticated", False):
            user_dto = UserDTO(
                id=user.id,
                email=user.email,
                client_type=getattr(user, "client_type", None),
                customer_number=getattr(user, "customer_number", None),
                is_b2b_verified=getattr(user, "is_b2b_verified", False),
            )

        promo = self.promo_port.get_applicable_promo(product_dto, user_dto)

        return PricingEngine.determine_price(product_dto, user_dto, promo)

    # Méthode de compatibilité avec l'ancienne interface de PricingService
    def compute_unit_price(self, product: ProductDTO, client_type: str | None = None) -> Decimal:
        """Compatibilité avec le contrat ``PricingService`` historique.

        Ici, ``product`` correspond au DTO minimal exposé par ``core.interfaces``.
        On ne dispose pas des grilles B2B ni des promos, donc on se
        contente de retourner ``product.unit_price``.
        """
        return getattr(product, "unit_price")

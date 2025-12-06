from __future__ import annotations

from decimal import Decimal
from typing import Optional

from typing import Iterable, Optional  # noqa: F401

from core.domain.dto import (
    ProductDTO,
    UserDTO,
    CartItemDTO,
    CartPricingResult,
)
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
    def get_unit_price(self, product: ProductDTO, user: Optional[UserDTO] = None) -> Decimal:
        """Calcule le prix unitaire final pour un produit donné.

        Cette méthode est la seule entrée publique du moteur de
        tarification.  Elle attend désormais un ``ProductDTO`` et un
        ``UserDTO`` (éventuellement ``None``) et retourne un ``Decimal``
        correspondant au prix final après application des promotions
        catalogue, de la grille B2B et des remises simples.  La
        signature ne dépend plus des modèles Django afin de maintenir
        l'isolation du domaine.
        """
        product_dto = product
        user_dto = user

        # Vérifie le cache avant de calculer le prix
        try:
            from django.core.cache import cache  # type: ignore
        except Exception:
            cache = None  # pragma: no cover
        cache_key = None
        if cache is not None:
            user_key = f"u{user_dto.id}" if user_dto is not None else "anon"
            cache_key = f"pricing:unit:{user_key}:{product_dto.id}"
            cached_price = cache.get(cache_key)
            if cached_price is not None:
                return Decimal(str(cached_price))

        promo = self.promo_port.get_applicable_promo(product_dto, user_dto)
        price = PricingEngine.determine_price(product_dto, user_dto, promo)
        # Sauvegarde en cache pour 10 minutes
        if cache is not None and cache_key is not None:
            cache.set(cache_key, str(price), 600)
        return price

    # Nouveauté : prévisualisation de prix avec quantité et règles avancées
    def preview_price(self, product, user=None, quantity: int = 1) -> Decimal:
        """Simule le calcul du prix pour une quantité donnée.

        Cette méthode ne s'appuie pas sur les promotions de catalogue
        ciblées (car l'adaptateur promo n'est pas disponible dans
        ``PricingEngine.determine_price_with_context``) mais applique
        l'ensemble des règles B2B, promotions simples et règles
        avancées (quantité, marque, famille, prix plancher).
        """
        # On délègue au moteur étendu pour la prévisualisation.
        from core.domain.pricing_engine import PricingEngine

        return PricingEngine.determine_price_with_context(product, user, quantity)

    # Méthode de compatibilité avec l'ancienne interface de PricingService
    def compute_unit_price(self, product: ProductDTO, client_type: str | None = None) -> Decimal:
        """Compatibilité avec le contrat ``PricingService`` historique.

        Ici, ``product`` correspond au DTO minimal exposé par ``core.interfaces``.
        On ne dispose pas des grilles B2B ni des promos, donc on se
        contente de retourner ``product.unit_price``.
        """
        # ``unit_price`` peut être défini par les repositories ou laissé
        # vide.  Si aucune valeur n'est présente on revient au prix public.
        if getattr(product, "unit_price", None) is not None:
            return Decimal(product.unit_price)
        return Decimal(product.price)

    def calculate_cart(
        self,
        items: Iterable[CartItemDTO],
        user: Optional[UserDTO] = None,
    ) -> CartPricingResult:
        """Calcule le prix de chaque ligne d'un panier et le total.

        Cette méthode centralise l'application des règles de promotions et
        de tarification.  Elle prend une liste d'``CartItemDTO`` contenant
        au minimum un ``product`` et une ``quantity`` et renvoie un
        ``CartPricingResult`` dans lequel chaque ligne comporte un
        ``unit_price`` et un ``total_price``.  Le total du panier est la
        somme de toutes les lignes.  Aucun calcul de prix ne doit être
        effectué en dehors de cette méthode.
        """
        priced_items: list[CartItemDTO] = []
        total = Decimal("0")
        for item in items:
            # Calcule le prix unitaire final pour le produit
            unit_price = self.get_unit_price(item.product, user)
            line_total = unit_price * Decimal(item.quantity)
            # Met à jour le produit.unit_price pour cohérence
            item.product.unit_price = unit_price
            priced_items.append(
                CartItemDTO(
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=unit_price,
                    total_price=line_total,
                )
            )
            total += line_total
        return CartPricingResult(items=priced_items, total=total)

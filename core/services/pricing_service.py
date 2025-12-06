from __future__ import annotations

from decimal import Decimal
from typing import Iterable, Optional, Union

from core.domain.dto import (
    ProductDTO,
    UserDTO,
    CartItemDTO,
    CartPricingResult,
)
from core.domain.pricing_engine import PricingEngine
from core.domain.pricing_rules import AdvancedPricingRules
from core.ports.promo_catalog_port import PromoCatalogPort


class PromoAwareB2BPricingService:
    """Service de pricing centralisé.

    Cette implémentation applique :

    1. Les promotions de catalogue ciblées par numéro client.
    2. La grille tarifaire B2B (wholesaler / big_retail / small_retail)
       avec surcharge +5 % pour les comptes non vérifiés.
    3. La promotion simple ``discount_price``.
    4. Le prix public ``price`` en dernier recours.

    Le domaine (``PricingEngine`` et ``pricing_rules``) ne manipule que
    des DTOs. Toute conversion depuis/vers les modèles Django est
    effectuée ici afin de préserver l'architecture hexagonale.
    """

    def __init__(self, promo_catalog_adapter: PromoCatalogPort) -> None:
        self.promo_port = promo_catalog_adapter

    # ------------------------------------------------------------------
    # Normalisation des entrées vers des DTOs
    # ------------------------------------------------------------------
    def _to_product_dto(self, product: Union[ProductDTO, object]) -> ProductDTO:
        """Convertit un objet produit en ``ProductDTO``.

        Si ``product`` est déjà un ``ProductDTO``, il est renvoyé tel quel.
        Sinon on construit un DTO minimal à partir des attributs du
        modèle Django (ou de tout autre objet duck-typed).
        """

        if isinstance(product, ProductDTO):
            return product

        return ProductDTO(
            id=getattr(product, "id"),
            sku=getattr(product, "article_code", "")
            or getattr(product, "sku", ""),
            price=getattr(product, "price"),
            discount_price=getattr(product, "discount_price", None),
            price_wholesaler=getattr(product, "price_wholesaler", None),
            price_big_retail=getattr(product, "price_big_retail", None),
            price_small_retail=getattr(product, "price_small_retail", None),
        )

    def _to_user_dto(self, user: Optional[Union[UserDTO, object]]) -> Optional[UserDTO]:
        """Convertit un utilisateur en ``UserDTO`` si nécessaire."""

        if user is None:
            return None
        if isinstance(user, UserDTO):
            return user

        # Objet Django ou équivalent
        if not getattr(user, "is_authenticated", False):
            return None

        return UserDTO(
            id=getattr(user, "id"),
            email=getattr(user, "email", ""),
            client_type=getattr(user, "client_type", None),
            customer_number=getattr(user, "customer_number", None),
            is_b2b_verified=getattr(user, "is_b2b_verified", False),
        )

    # ------------------------------------------------------------------
    # API principale utilisée par le reste du système
    # ------------------------------------------------------------------
    def get_unit_price(self, product, user: Optional[object] = None) -> Decimal:
        """Calcule le prix unitaire final pour un produit donné.

        Cette méthode est la seule entrée publique du moteur de
        tarification côté application. Elle accepte soit des modèles
        Django, soit des DTOs, mais convertit systématiquement ces
        objets en ``ProductDTO`` / ``UserDTO`` avant d'appeler le
        domaine.
        """

        product_dto = self._to_product_dto(product)
        user_dto = self._to_user_dto(user)

        # Vérifie le cache avant de calculer le prix
        try:  # pragma: no cover - cache absent hors contexte Django
            from django.core.cache import cache  # type: ignore
        except Exception:  # pragma: no cover
            cache = None
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

    # ------------------------------------------------------------------
    # Prévisualisation de prix avec quantité et règles avancées
    # ------------------------------------------------------------------
    def preview_price(self, product, user=None, quantity: int = 1) -> Decimal:
        """Simule le calcul du prix pour une quantité donnée.

        Cette méthode accepte encore un ``product`` Django pour des
        raisons de compatibilité avec les couches de présentation, mais
        elle convertit immédiatement l'objet en DTO côté domaine. Les
        règles avancées (quantité, marque, famille, plancher) sont
        ensuite appliquées en utilisant uniquement les informations
        nécessaires (slug de marque, nom de catégorie, prix public).
        """

        # Prix unitaire de base via le moteur pur (DTO only)
        base_unit_price = self.get_unit_price(product, user)

        # Extraction des informations nécessaires pour les règles avancées
        brand = getattr(product, "brand", None)
        brand_slug = getattr(brand, "slug", None)
        brand_name = getattr(brand, "name", None)
        category = getattr(product, "category", None)
        category_name = getattr(category, "name", None)
        public_price = getattr(product, "price", None)

        # Application des règles avancées dans l'ordre désiré.
        final_price = AdvancedPricingRules.apply_quantity_discount(base_unit_price, quantity)
        final_price = AdvancedPricingRules.apply_brand_discount(
            final_price,
            brand_slug=brand_slug,
            brand_name=brand_name,
        )
        final_price = AdvancedPricingRules.apply_family_discount(
            final_price,
            category_name=category_name,
        )
        final_price = AdvancedPricingRules.apply_floor(final_price, public_price)
        return final_price

    # ------------------------------------------------------------------
    # Méthodes de compatibilité / agrégats
    # ------------------------------------------------------------------
    def compute_unit_price(self, product: ProductDTO, client_type: str | None = None) -> Decimal:
        """Compatibilité avec le contrat ``PricingService`` historique.

        Ici, ``product`` correspond au DTO minimal exposé par
        ``core.interfaces``. On ne dispose pas des grilles B2B ni des
        promos, donc on se contente de retourner ``product.unit_price``.
        """
        # ``unit_price`` peut être défini par les repositories ou laissé
        # vide. Si aucune valeur n'est présente on revient au prix public.
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
        de tarification. Elle prend une liste de ``CartItemDTO`` contenant
        au minimum un ``product`` et une ``quantity`` et renvoie un
        ``CartPricingResult`` dans lequel chaque ligne comporte un
        ``unit_price`` et un ``total_price``. Le total du panier est la
        somme de toutes les lignes. Aucun calcul de prix ne doit être
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

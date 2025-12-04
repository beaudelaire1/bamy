from decimal import Decimal
from typing import Optional

from core.domain.pricing_rules import B2BPricingRules
from core.domain.dto import ProductDTO, UserDTO, PromoItemDTO


class PricingEngine:
    """Moteur central de calcul du prix unitaire.

    Ordre d'application global (obligatoire) :

    1. Promo catalogue ciblée (si applicable)  -> prix final
    2. Grille B2B                              -> prix final
    3. Promo simple (discount_price)          -> prix final
    4. Prix public (price)                    -> fallback
    """

    @staticmethod
    def determine_price(
        product_dto: ProductDTO,
        user_dto: Optional[UserDTO] = None,
        promo_item_dto: Optional[PromoItemDTO] = None,
    ) -> Decimal:
        # 1. Promo catalogue ciblée
        if promo_item_dto is not None:
            return promo_item_dto.promo_price

        # 2. Grille B2B
        price_b2b = B2BPricingRules.apply(user_dto, product_dto) if user_dto is not None else None
        if price_b2b is not None:
            return price_b2b

        # 3. Promo simple (discount_price)
        discount = getattr(product_dto, "discount_price", None)
        if discount is not None:
            discount = Decimal(discount)
            base_price = Decimal(product_dto.price)
            if Decimal("0") < discount < base_price:
                return discount

        # 4. Prix public
        return Decimal(product_dto.price)

    @staticmethod
    def determine_price_with_context(
        product,
        user: Optional[object] = None,
        quantity: int = 1,
    ) -> Decimal:
        """Calcule le prix unitaire en tenant compte de règles avancées.

        Cette méthode accepte directement les objets Django ``product`` et
        ``user`` plutôt que des DTOs et applique toutes les règles de
        tarification (promotions, grille B2B, remises simples) puis les
        remises avancées (quantité, marque, famille) ainsi que le
        respect d'un prix plancher.

        :param product: produit Django pour lequel le prix doit être calculé
        :param user: utilisateur Django effectuant l'achat (peut être None)
        :param quantity: quantité commandée pour appliquer les remises par quantité
        :returns: prix unitaire final après application de toutes les règles
        """
        # Construire les DTOs existants pour réutiliser la logique de base
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

        # Aucune promotion catalogue ciblée n'est prise en compte ici car
        # l'adaptateur promo n'est pas disponible dans ce contexte.
        base_unit_price = PricingEngine.determine_price(product_dto, user_dto, None)
        # Application des règles avancées
        from core.domain.pricing_rules import AdvancedPricingRules  # import différé pour éviter les cycles

        final_price = AdvancedPricingRules.apply_quantity_discount(base_unit_price, quantity)
        final_price = AdvancedPricingRules.apply_brand_discount(final_price, product, quantity)
        final_price = AdvancedPricingRules.apply_family_discount(final_price, product, quantity)
        final_price = AdvancedPricingRules.apply_floor(final_price, product)
        return final_price

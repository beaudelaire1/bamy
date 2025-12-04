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

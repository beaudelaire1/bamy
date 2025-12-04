
from core.domain.pricing_rules import B2BPricingRules

class PricingEngine:
    @staticmethod
    def determine_price(product_dto, user_dto, promo_item_dto=None):
        if promo_item_dto:
            return promo_item_dto.promo_price
        price_b2b = B2BPricingRules.apply(user_dto, product_dto)
        return price_b2b

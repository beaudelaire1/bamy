
class B2BPricingRules:
    @staticmethod
    def apply(user, product):
        if user.client_type == "wholesaler" and product.price_wholesaler:
            return product.price_wholesaler
        if user.client_type == "big_retail" and product.price_big_retail:
            return product.price_big_retail
        if not user.is_verified:
            return product.price * 1.05
        return product.price

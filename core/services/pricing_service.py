
from core.adapters.orm_promo_adapter import DjangoPromoCatalogAdapter
from core.domain.pricing_engine import PricingEngine
from core.domain.dto import ProductDTO, UserDTO

class PricingService:
    promo_port = DjangoPromoCatalogAdapter()

    @staticmethod
    def calculate_price(product, user):
        product_dto = ProductDTO(
            id=product.id,
            sku=getattr(product,'sku',''),
            price=product.price,
            price_wholesaler=getattr(product,'price_wholesaler',None),
            price_big_retail=getattr(product,'price_big_retail',None),
        )
        user_dto = UserDTO(
            id=user.id,
            email=user.email,
            client_type=getattr(user,'client_type',None),
            is_verified=getattr(user,'is_verified',True),
        )
        promo = PricingService.promo_port.get_applicable_promo(product_dto, user_dto)
        return PricingEngine.determine_price(product_dto, user_dto, promo)

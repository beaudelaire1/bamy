from decimal import Decimal

from core.domain.dto import ProductDTO, UserDTO, PromoItemDTO
from core.domain.pricing_engine import PricingEngine


def _make_product(**kwargs) -> ProductDTO:
    base = dict(
        id=1,
        sku="TEST",
        price=Decimal("100.00"),
        discount_price=None,
        price_wholesaler=None,
        price_big_retail=None,
        price_small_retail=None,
    )
    base.update(kwargs)
    return ProductDTO(**base)


def _make_user(**kwargs) -> UserDTO:
    base = dict(
        id=1,
        email="test@example.com",
        client_type="wholesaler",
        customer_number="CUST001",
        is_b2b_verified=True,
    )
    base.update(kwargs)
    return UserDTO(**base)


def test_catalog_promo_has_priority():
    product = _make_product()
    user = _make_user()
    promo = PromoItemDTO(promo_price=Decimal("42.00"))

    price = PricingEngine.determine_price(product, user, promo)
    assert price == Decimal("42.00")


def test_b2b_applied_when_no_catalog():
    product = _make_product(price_wholesaler=Decimal("80.00"))
    user = _make_user(client_type="wholesaler")

    price = PricingEngine.determine_price(product, user, None)
    assert price == Decimal("80.00")


def test_simple_discount_when_no_b2b():
    product = _make_product(price=Decimal("100.00"), discount_price=Decimal("90.00"))
    user = _make_user(client_type="regular")

    price = PricingEngine.determine_price(product, user, None)
    assert price == Decimal("90.00")


def test_public_price_as_fallback():
    product = _make_product(price=Decimal("100.00"), discount_price=None)
    user = _make_user(client_type="regular")

    price = PricingEngine.determine_price(product, user, None)
    assert price == Decimal("100.00")


def test_unverified_b2b_has_surcharge():
    product = _make_product(price_wholesaler=Decimal("80.00"))
    user = _make_user(client_type="wholesaler", is_b2b_verified=False)

    price = PricingEngine.determine_price(product, user, None)
    assert price == Decimal("84.00")  # 80 * 1.05

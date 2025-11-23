from __future__ import annotations

from decimal import Decimal

from core.interfaces import PricingService, ProductDTO


class SimplePricingService(PricingService):
    """
    Service de tarification minimal.

    Pour le moment, applique simplement le prix du produit. Cette
    classe est le point d'extension naturel pour introduire des
    grilles tarifaires B2B ou des segments de clients.
    """

    def compute_unit_price(self, product: ProductDTO, client_type: str | None = None) -> Decimal:
        return product.unit_price

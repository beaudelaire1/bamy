from __future__ import annotations

from decimal import Decimal
from typing import Iterable

from catalog.models import Product
from core.interfaces import ProductRepository, ProductDTO


class DjangoProductRepository(ProductRepository):
    """
    Implémentation du repository produit basée sur le modèle Django catalog.Product.
    """

    def _to_dto(self, obj: Product) -> ProductDTO:
        """Convert a Django ``Product`` instance into a ``ProductDTO``.

        The DTO exposes all pricing related fields along with
        merchandising attributes.  The ``unit_price`` is initialised
        with the discount price if present, otherwise the public
        ``price``.  This field will be recomputed by the pricing
        service when necessary.
        """
        # Public price fields
        base_price = getattr(obj, "price", None)
        discount = getattr(obj, "discount_price", None)
        # B2B grid values, they may not exist on older models
        wholesaler = getattr(obj, "price_wholesaler", None)
        big_retail = getattr(obj, "price_big_retail", None)
        small_retail = getattr(obj, "price_small_retail", None)
        # Choose the most specific price as the initial unit_price
        unit = discount or base_price
        return ProductDTO(
            id=obj.id,
            sku=obj.article_code or str(obj.pk),
            price=base_price,
            discount_price=discount,
            price_wholesaler=wholesaler,
            price_big_retail=big_retail,
            price_small_retail=small_retail,
            title=getattr(obj, "title", None),
            is_active=getattr(obj, "is_active", None),
            unit_price=unit,
        )

    def get_by_id(self, product_id: int) -> ProductDTO:
        obj = Product.objects.get(pk=product_id, is_active=True)
        return self._to_dto(obj)

    def get_by_sku(self, sku: str) -> ProductDTO:
        obj = Product.objects.get(article_code=sku, is_active=True)
        return self._to_dto(obj)

    def search(self, query: str | None = None) -> Iterable[ProductDTO]:
        qs = Product.objects.filter(is_active=True)
        if query:
            from django.db.models import Q

            qs = qs.filter(
                Q(title__icontains=query)
                | Q(article_code__icontains=query)
                | Q(ean__icontains=query)
            )
        return [self._to_dto(p) for p in qs.order_by("-updated_at")[:100]]

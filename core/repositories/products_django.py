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
        price = obj.discount_price or obj.price
        return ProductDTO(
            id=obj.id,
            sku=obj.article_code or str(obj.pk),
            title=obj.title,
            unit_price=price,
            is_active=obj.is_active,
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

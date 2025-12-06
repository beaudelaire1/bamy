from __future__ import annotations

from typing import Iterable

from core.interfaces import ProductRepository, ProductDTO
from catalog.models import Product
from django.db.models import Q


class ProductService:
    """
    Service métier pour la consultation des produits.
    """

    def __init__(self, product_repo: ProductRepository) -> None:
        self.product_repo = product_repo

    def search(self, query: str | None = None) -> Iterable[ProductDTO]:
        """
        Recherche métier retournant des DTO. Utilisée par la couche
        domaine ou d'autres services.
        """
        return self.product_repo.search(query)

    def search_queryset_for_api(
        self, query: str | None = None, limit: int = 20
    ):
        """
        Variante orientée API qui retourne un queryset Django filtré.

        Cette méthode est utilisée par les vues REST pour éviter que
        celles-ci ne dépendent directement du modèle ``Product``. La
        logique de filtrage est centralisée ici.
        """
        qs = Product.objects.filter(is_active=True)
        if query:
            qs = qs.filter(
                Q(title__icontains=query)
                | Q(article_code__icontains=query)
                | Q(ean__icontains=query)
            )
        return qs.order_by("-updated_at")[:limit]

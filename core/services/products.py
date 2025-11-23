from __future__ import annotations

from typing import Iterable

from core.interfaces import ProductRepository, ProductDTO


class ProductService:
    """
    Service métier pour la consultation des produits.
    """

    def __init__(self, product_repo: ProductRepository) -> None:
        self.product_repo = product_repo

    def search(self, query: str | None = None) -> Iterable[ProductDTO]:
        return self.product_repo.search(query)

"""
Resources pour l'import/export de données via django-import-export.

Chaque classe définit le modèle associé et les champs qui seront
importés/exportés lors des opérations en masse.  Ces ressources sont
utilisées par l'admin pour permettre l'import de fichiers Excel/CSV.
"""

from import_export import resources
from .models import Category, Brand, Product


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "parent", "is_active")
        import_id_fields = ("id",)


class BrandResource(resources.ModelResource):
    class Meta:
        model = Brand
        fields = ("id", "name", "slug", "is_active")
        import_id_fields = ("id",)


class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        exclude = ("created_at", "updated_at")
        import_id_fields = ("id",)
        # on précise les relations pour que l'import fonctionne via noms
        # au lieu d'identifiants internes
        fields = (
            "id",
            "article_code",
            "ean",
            "title",
            "slug",
            "brand",
            "category",
            "price",
            "discount_price",
            "price_wholesaler",
            "price_big_retail",
            "price_small_retail",
            "stock",
            "min_order_qty",
            "pcb_qty",
            "order_in_packs",
            "is_week_selection",
            "selection_start",
            "selection_end",
            "unit",
            "image",
        )
        import_id_fields = ("id",)
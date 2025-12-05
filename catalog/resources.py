"""
Resources pour l'import/export de données via django-import-export.

Chaque classe définit le modèle associé et les champs importés/exportés.
Ce fichier corrige les problèmes de :
- category_id NULL
- doublons SKU / article_code
- import Brand via id au lieu du nom
- import Category via id au lieu du nom
"""

from import_export import resources, fields
from import_export.widgets import (
    ForeignKeyWidget,
    DateWidget,
    BooleanWidget,
    DecimalWidget,
)
from .models import Category, Brand, Product


# -------------------------------------------------------
#  CATEGORY RESOURCE
# -------------------------------------------------------
class CategoryResource(resources.ModelResource):
    parent = fields.Field(
        column_name="parent",
        attribute="parent",
        widget=ForeignKeyWidget(Category, field="name"),
        default=None,
    )

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "parent", "is_active")
        import_id_fields = ("id",)
        skip_unchanged = True
        report_skipped = True


# -------------------------------------------------------
#  BRAND RESOURCE
# -------------------------------------------------------
class BrandResource(resources.ModelResource):
    class Meta:
        model = Brand
        fields = ("id", "name", "slug", "is_active")
        import_id_fields = ("id",)
        skip_unchanged = True
        report_skipped = True


# -------------------------------------------------------
#  PRODUCT RESOURCE
# -------------------------------------------------------
class ProductResource(resources.ModelResource):

    # IMPORT DES RELATIONS VIA LE NOM (PAS ID)
    brand = fields.Field(
        column_name="brand",
        attribute="brand",
        widget=ForeignKeyWidget(Brand, field="name"),
    )

    category = fields.Field(
        column_name="category",
        attribute="category",
        widget=ForeignKeyWidget(Category, field="name"),
        default=None,
    )

    # DATES
    selection_start = fields.Field(
        column_name="selection_start",
        attribute="selection_start",
        widget=DateWidget(format="%Y-%m-%d"),
    )

    selection_end = fields.Field(
        column_name="selection_end",
        attribute="selection_end",
        widget=DateWidget(format="%Y-%m-%d"),
    )

    # DECIMAUX
    price = fields.Field(
        column_name="price",
        attribute="price",
        widget=DecimalWidget(),
    )

    discount_price = fields.Field(
        column_name="discount_price",
        attribute="discount_price",
        widget=DecimalWidget(),
    )

    # BOOLÉENS
    order_in_packs = fields.Field(
        column_name="order_in_packs",
        attribute="order_in_packs",
        widget=BooleanWidget(),
    )

    is_week_selection = fields.Field(
        column_name="is_week_selection",
        attribute="is_week_selection",
        widget=BooleanWidget(),
    )

    def before_import_row(self, row, **kwargs):
        if row.get("image"):
            row["image"] = f"products/{row['image']}"

    class Meta:
        model = Product
        import_id_fields = ("article_code",)  # ❗ UNIQUE & FIABLE
        exclude = ("created_at", "updated_at")
        skip_unchanged = True
        report_skipped = True

        fields = (
            "article_code",
            "ean",
            "title",
            "sku",
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


    # ---------------------------------------------------
    #  HOOKS
    # ---------------------------------------------------
    def before_import_row(self, row, **kwargs):
        """
        - Génère un SKU automatiquement si absent
        - Évite les doublons violant UNIQUE(sku)
        """
        if not row.get("sku") and row.get("article_code"):
            row["sku"] = row["article_code"]

    def before_save_instance(self, instance, row, **kwargs):
        """
        - Regénère un slug à partir du titre + sku
        - Corrige brand/category manquants
        """

        # Slug auto
        if not instance.slug:
            from django.utils.text import slugify
            instance.slug = slugify(f"{instance.title}-{instance.sku}")

        # Si category introuvable → None (nullable OK)
        if not instance.category_id:
            instance.category = None


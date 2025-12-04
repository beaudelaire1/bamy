from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Brand, Product

# Importer les ressources pour l'import/export si django-import-export est installé
try:
    from import_export import resources  # type: ignore
    from .resources import CategoryResource, BrandResource, ProductResource  # type: ignore
except Exception:
    CategoryResource = None  # type: ignore
    BrandResource = None  # type: ignore
    ProductResource = None  # type: ignore

# Si la bibliothèque import_export est disponible, on l'utilise pour
# permettre l'import/export en masse de produits, marques et catégories
# depuis des fichiers Excel/CSV. Sinon, on retombe sur la classe
# ``ModelAdmin`` standard.
try:
    from import_export.admin import ImportExportModelAdmin  # type: ignore
    BaseAdmin = ImportExportModelAdmin
except Exception:
    BaseAdmin = admin.ModelAdmin

@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    list_display = ("name", "parent", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    # Associe une ressource pour permettre l'import/export
    if CategoryResource:
        resource_class = CategoryResource

@admin.register(Brand)
class BrandAdmin(BaseAdmin):
    list_display = ("name", "is_active", "logo_preview")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("logo_preview",)

    fieldsets = (
        (None, {"fields": ("name", "slug", "is_active")}),
        ("Logo", {"fields": ("logo", "logo_preview")}),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="height:40px;border-radius:8px;">', obj.logo.url)
        return "—"
    logo_preview.short_description = "Logo"

    # Association de la ressource d'import/export pour Brand
    if BrandResource:
        resource_class = BrandResource

@admin.register(Product)
class ProductAdmin(BaseAdmin):
    """Personnalisation de l'interface d'administration pour les produits."""

    list_display = (
        "article_code",
        "ean",
        "title",
        "brand",
        "category",
        "price",
        "discount_price",
        "price_wholesaler",
        "price_big_retail",
        "price_small_retail",
        "pcb_qty",
        "unit",
        "is_week_selection",
    )
    fieldsets = (
        (
            "Infos",
            {
                "fields": (
                    "article_code",
                    "ean",
                    "title",
                    "brand",
                    "category",
                    "image",
                    "stock",
                    "slug",
                    "unit",
                )
            },
        ),
        (
            "Tarifs",
            {
                "fields": (
                    "price",
                    "discount_price",
                    "price_wholesaler",
                    "price_big_retail",
                    "price_small_retail",
                )
            },
        ),
        ("Quantités", {"fields": ("min_order_qty", "pcb_qty", "order_in_packs")}),
        (
            "Sélection semaine",
            {
                "fields": ("is_week_selection", "selection_start", "selection_end"),
            },
        ),
    )
    list_filter = (
        "brand",
        "category",
        "is_active",
        "is_week_selection",
    )
    search_fields = (
        "title",
        "sku",
        "ean",
        "article_code",
        "brand__name",
        "category__name",
    )
    readonly_fields = ("created_at", "updated_at")
    prepopulated_fields = {"slug": ("title",)}

    # Ressource d'import/export pour Product
    if ProductResource:
        resource_class = ProductResource

# Promo Management
from .models import PromoCatalog, PromoItem
admin.site.register(PromoCatalog)
admin.site.register(PromoItem)

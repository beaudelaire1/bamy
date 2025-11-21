from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Brand, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
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

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Personnalisation de l'interface d'administration pour les produits."""

    list_display = (
        "article_code",
        "ean",
        "title",
        "brand",
        "category",
        "price",
        "discount_price",
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
        ("Tarifs", {"fields": ("price", "discount_price")}),
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

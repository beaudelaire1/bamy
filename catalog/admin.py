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

# -----------------------------------------------------------------------------
# Gestion des promotions
#
# Le modèle ``PromoItem`` contient un champ JSON ``allowed_customer_numbers``
# qui stocke une liste de numéros de client autorisés pour une promotion.
# Dans l'admin Django, on souhaite offrir une expérience plus intuitive que
# l'édition brute de JSON. Pour cela, on définit un formulaire dédié qui
# présente ce champ sous forme de zone de texte, une ligne par numéro. Lors de
# l'enregistrement du formulaire, on transforme automatiquement ces lignes en
# une liste Python qui sera sérialisée en JSON par Django. Inversement, lors
# de l'affichage initial, si la valeur est déjà une liste, on la joint avec
# des sauts de ligne.

from django import forms


class PromoItemForm(forms.ModelForm):
    """
    Formulaire personnalisé pour ``PromoItem`` afin de rendre l'édition du
    champ ``allowed_customer_numbers`` plus conviviale.

    Au lieu de laisser Django afficher un champ JSON brut, on utilise un
    ``CharField`` avec un ``Textarea``. Chaque ligne correspond à un numéro de
    client. Lors de la validation, on découpe les lignes en liste. En
    affichage initial, si la valeur est une liste, on la convertit en chaîne
    multilignes.
    """

    allowed_customer_numbers = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text=(
            "Numéros de client autorisés pour cette promotion. \
            Entrez un numéro par ligne; laissez vide pour aucune restriction."
        ),
        label="Numéros clients autorisés",
    )

    class Meta:
        model = PromoItem
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si la valeur initiale est une liste, on la rend lisible par l'utilisateur
        init_val = self.initial.get("allowed_customer_numbers")
        if isinstance(init_val, list):
            self.initial["allowed_customer_numbers"] = "\n".join(str(v) for v in init_val)

    def clean_allowed_customer_numbers(self):
        data = self.cleaned_data.get("allowed_customer_numbers") or ""
        # Découpe en lignes non vides et supprime les espaces superflus
        numbers = [line.strip() for line in data.splitlines() if line.strip()]
        return numbers


@admin.register(PromoCatalog)
class PromoCatalogAdmin(admin.ModelAdmin):
    """Administration basique du catalogue de promotions."""
    list_display = ("title", "start_date", "end_date", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title",)


@admin.register(PromoItem)
class PromoItemAdmin(admin.ModelAdmin):
    """
    Administration personnalisée pour les items de promotions.

    Utilise ``PromoItemForm`` pour gérer le champ JSON des numéros de clients
    autorisés via un widget convivial.
    """

    form = PromoItemForm
    list_display = ("catalog", "product", "promo_price")
    list_filter = ("catalog",)
    search_fields = ("product__title", "product__sku")


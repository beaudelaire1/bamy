from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
from math import ceil
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.db.models import F, Q, Manager, QuerySet

def unique_slugify(instance, value, slug_field_name="slug"):
    slug = slugify(value)
    ModelClass = instance.__class__
    unique_slug = slug
    counter = 2
    while ModelClass.objects.filter(**{slug_field_name: unique_slug}).exclude(pk=instance.pk).exists():
        unique_slug = f"{slug}-{counter}"
        counter += 1
    setattr(instance, slug_field_name, unique_slug)

class Category(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    parent = models.ForeignKey("self", null=True, blank=True, related_name="children", on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            unique_slugify(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:category", args=[self.slug])

class Brand(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    # LOGO UNIQUEMENT
    logo = models.ImageField(upload_to="brands/logos/", blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            unique_slugify(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:brand", args=[self.slug])


class ProductQuerySet(QuerySet):
    def promotions(self):
        """
        Retourne uniquement les produits réellement en promo :
        - discount_price non nul
        - discount_price > 0
        - discount_price < price
        """
        return (self
                .filter(discount_price__isnull=False)
                .exclude(discount_price=Decimal("0"))
                .filter(discount_price__lt=F("price")))

class ProductManager(Manager.from_queryset(ProductQuerySet)):
    pass

class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=270, unique=True, blank=True)
    sku = models.CharField("Référence", max_length=64, unique=True)

    # Champs supplémentaires pour l'intégration de données externes
    # Le code article est un identifiant produit unique fourni par
    # le fournisseur externe. Il est distinct du SKU interne, mais il
    # peut être utilisé pour faire correspondre un produit lors de
    # l'importation. On le déclare comme unique pour empêcher des
    # doublons accidentels. Dans le cas où l'import ne fournit pas
    # explicitement de SKU, on pourra initialiser ce dernier à partir
    # du code article.
    article_code = models.CharField(
        "Code article",
        max_length=32,
        unique=True,
        help_text=(
            "Identifiant unique du produit fourni par le grossiste. "
            "Nous autorisons désormais jusqu'à 32 caractères pour couvrir les cas où "
            "la référence fournisseur dépasse 7 caractères."
        ),
    )
    # Le code EAN (European Article Number) est optionnel mais permet
    # d'identifier de manière standardisée le produit. La contrainte
    # length de 14 permet d'accueillir les formats courants (13 ou 8).
    ean = models.CharField(
        "EAN",
        max_length=14,
        blank=True,
        null=True,
        help_text="Code-barres international du produit.",
    )
    # Le code PCB fait référence au code du constructeur (Pack/Carton).
    # Ce champ est optionnel car il n'est pas toujours fourni par le
    # grossiste. Lorsque présent, il peut aider à rapprocher les lots.
    pcb_code = models.CharField(
        "Code PCB",
        max_length=64,
        blank=True,
        null=True,
        help_text="Référence constructeur (PCB) pour le produit.",
    )
    category = models.ForeignKey(Category, related_name="products", on_delete=models.PROTECT)
    brand = models.ForeignKey(Brand, related_name="products", on_delete=models.PROTECT)
    short_description = models.CharField(max_length=300, blank=True, default="")
    description = CKEditor5Field("Description", blank=True, null=True, config_name="default")

    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    # Informations logistiques supplémentaires
    # Exemple : "Carton de 6", "Palette", etc.  Ce champ permet d'indiquer l'unité
    # de conditionnement pour les clients professionnels.
    unit = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Unité de conditionnement (ex. carton de 6)",
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    min_order_qty = models.PositiveIntegerField(default=10, help_text="Quantité minimale par commande (MOQ).")
    pcb_qty = models.PositiveIntegerField(default=1, help_text="Quantité par PCB (lot/colis).")
    order_in_packs = models.BooleanField(default=False, help_text="Si vrai, commande uniquement par multiples de PCB.")

    # Sélection de la semaine
    # Indique qu'un produit est mis en avant pour une période donnée. Lorsque ce
    # champ est activé, le produit figure sur la page "sélection de la semaine".
    is_week_selection = models.BooleanField(default=False, help_text="Produit sélectionné de la semaine")
    selection_start = models.DateField(null=True, blank=True)
    selection_end = models.DateField(null=True, blank=True)

    @property
    def is_promo(self) -> bool:
        """
        Indique si le produit est réellement en promotion.

        Un produit est en promotion lorsque un prix promotionnel est défini,
        supérieur à zéro et strictement inférieur au prix normal. Cette
        propriété est utilisée à plusieurs endroits dans les templates pour
        afficher un badge « Promo » et pour calculer le prix final.
        """
        return (
            self.discount_price is not None
            and self.discount_price > 0
            and self.discount_price < self.price
        )

    def adjust_order_qty(self, requested: int) -> int:
        """
        Corrige la quantité demandée selon le MOQ et/ou les multiples de PCB.
        Règles:
          - minimum = max(1, min_order_qty, pcb_qty si order_in_packs)
          - si order_in_packs => arrondi au multiple supérieur de pcb_qty
        """
        if requested is None or requested <= 0:
            requested = 10
        base_min = max(10, int(self.min_order_qty or 10), int(self.pcb_qty or 10) if self.order_in_packs else 10)
        qty = max(requested, base_min)
        if self.order_in_packs and self.pcb_qty > 10:
            # arrondi au multiple de pcb_qty supérieur
            m = int(self.pcb_qty)
            qty = ceil(qty / m) * m
        return qty

    @property
    def initial_order_qty(self) -> int:
        """Quantité proposée par défaut au clic 'Ajouter'."""
        return self.adjust_order_qty(10)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["price"]),
            models.Index(fields=["discount_price"]),

        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = f"{self.title}-{self.sku}"
            unique_slugify(self, base)
        super().save(*args, **kwargs)

    @property
    def final_price(self):
        return self.discount_price if self.discount_price else self.price

    def get_absolute_url(self):
        return reverse("catalog:product_detail", args=[self.slug])

    objects = ProductManager()  # remplace le Manager par défaut

    # La propriété is_promo est définie plus haut. La redéfinition ci‑dessous
    # était un duplicata et a été supprimée afin d'éviter de masquer la
    # définition précédente. Laisser une redéfinition sans modification
    # provoquerait des incohérences lors du calcul de la promotion.

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def clean(self):
        # Validation côté serveur, si tu veux garder un garde-fou
        super().clean()
        if self.discount_price is not None:
            if self.discount_price <= 0:
                raise ValidationError({"discount_price": "Le prix promo doit être > 0."})
            if self.discount_price >= self.price:
                raise ValidationError({"discount_price": "Le prix promo doit être inférieur au prix normal."})


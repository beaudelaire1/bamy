from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone

from clients.models import Client
from catalog.models import Product


class Quote(models.Model):
    """Modèle représentant un devis en attente de validation.

    Un devis est créé par un utilisateur (authentifié) pour le compte
    d'un client.  Il contient une ou plusieurs lignes de produits et
    peut être validé par un manager afin de devenir une commande.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Brouillon"
        PENDING = "pending", "En attente de validation"
        APPROVED = "approved", "Approuvé"
        REJECTED = "rejected", "Rejeté"
        ORDERED = "ordered", "Transformé en commande"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quotes",
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="quotes",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    validated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "devis"
        verbose_name_plural = "devis"

    def __str__(self) -> str:
        return f"Quote #{self.pk} ({self.get_status_display()})"

    @property
    def subtotal(self) -> Decimal:
        return sum((item.line_total for item in self.items.all()), Decimal("0.00"))


class QuoteItem(models.Model):
    """Ligne d'un devis.

    Capture le prix appliqué au moment de la création du devis afin
    d'assurer la traçabilité des conditions tarifaires.
    """

    quote = models.ForeignKey(Quote, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Calcul automatique du total de ligne si non fourni
        if not self.unit_price:
            # fallback pour s'assurer d'avoir un prix, utilise prix public
            self.unit_price = self.product.price
        self.line_total = (Decimal(self.unit_price) * Decimal(self.quantity)).quantize(Decimal("0.01"))
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.product.title} x{self.quantity}"

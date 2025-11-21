from django.db import models


class Customer(models.Model):
    """
    Représente un client ou prospect.

    Un client peut être un magasin partenaire (B2B) ou un particulier (B2C).
    Les informations stockées ici permettent de suivre les commandes et
    d'améliorer la relation commerciale.
    """

    email = models.EmailField(unique=True)
    first_name = models.CharField("Prénom", max_length=100, blank=True)
    last_name = models.CharField("Nom", max_length=100, blank=True)
    company = models.CharField("Entreprise", max_length=200, blank=True)
    phone = models.CharField("Téléphone", max_length=50, blank=True)
    address = models.CharField("Adresse", max_length=255, blank=True)
    postal_code = models.CharField("Code postal", max_length=5, blank=True)
    client_type = models.CharField(
        "Type de client",
        max_length=20,
        choices=[
            ("B2C", "Particulier"),
            ("B2B", "Professionnel"),
            ("Prospect", "Prospect"),
            ("Other", "Autre"),
        ],
        default="B2C",
    )
    store_type = models.CharField(
        "Type de magasin",
        max_length=50,
        choices=[
            ("Retail", "Petite distribution"),
            ("Specialty", "Magasin spécialisé"),
            ("Franchise", "Franchise"),
            ("Distributor", "Grande distribution"),
            ("Wholesale", "Grossiste"),
            ("Other", "Autre"),
        ],
        default="Retail"
    )
    client_code = models.CharField(
        "Code client", max_length=5, blank=True, unique=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField("Notes", blank=True)

    class Meta:
        verbose_name = "client"
        verbose_name_plural = "clients"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip() or self.email
        return self.email


# -----------------------------------------------------------------------------
# Demandes de devis (QuoteRequest)

from django.conf import settings
from django.utils import timezone


class QuoteRequest(models.Model):
    """
    Modèle pour stocker les demandes de devis.

    Chaque demande comprend des informations de contact et une liste de
    références/quantités demandées.  L'attribut `items` est stocké au
    format texte (une référence par ligne) pour simplicité de saisie
    et de stockage.  Un envoi d'email est déclenché à la création
    depuis la vue correspondante.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quote_requests",
    )
    email = models.EmailField()
    company = models.CharField(max_length=255, blank=True, default="")
    first_name = models.CharField(max_length=100, blank=True, default="")
    last_name = models.CharField(max_length=100, blank=True, default="")
    phone = models.CharField(max_length=50, blank=True, default="")
    items = models.TextField("Références et quantités")
    comment = models.TextField("Commentaire", blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "demande de devis"
        verbose_name_plural = "demandes de devis"

    def __str__(self) -> str:
        return f"Devis #{self.pk} par {self.email}"
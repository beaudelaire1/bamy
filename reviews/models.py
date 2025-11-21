"""Modèles pour les avis produits.

Cette application permet aux utilisateurs de laisser des notes et des
commentaires sur les produits. Les avis sont publiés sous
modération dans une version future, mais cette première itération
enregistre simplement les commentaires.
"""

from django.db import models
from django.conf import settings
from catalog.models import Product


class Review(models.Model):
    """Avis d'un utilisateur sur un produit.

    Un avis comporte une note sur 5, un commentaire facultatif et
    une référence au produit et à l'utilisateur (optionnel pour le
    cas des commandes invitées).
    """

    product = models.ForeignKey(Product, related_name="reviews", on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="product_reviews"
    )
    rating = models.PositiveSmallIntegerField(help_text="Note sur 5")
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Avis de {self.user or 'invité'} ({self.rating}/5)"
"""Modèles pour le programme de fidélité.

Ces modèles permettent de suivre le nombre de points de fidélité
attribués aux utilisateurs et de gérer des coupons promotionnels.
"""

from django.db import models
from django.conf import settings


class LoyaltyAccount(models.Model):
    """Compte fidélité lié à un utilisateur.

    Les points sont augmentés lors des achats et peuvent être
    consommés pour obtenir des réductions.
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="loyalty_account")
    points = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Fidélité de {self.user}: {self.points} pts"

    def add_points(self, amount: int) -> None:
        self.points = models.F('points') + amount
        self.save(update_fields=["points"])


class Coupon(models.Model):
    """Coupon promotionnel utilisable par les clients.

    Un coupon peut proposer soit une remise en pourcentage, soit une
    remise fixe en monnaie. Il possède une date d'expiration.
    """

    DISCOUNT_TYPE_CHOICES = [
        ("fixed", "Remise fixe"),
        ("percent", "Remise en pourcentage"),
    ]

    code = models.CharField(max_length=20, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, default="percent")
    discount_value = models.DecimalField(max_digits=6, decimal_places=2)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"Coupon {self.code} ({self.discount_value}{'%' if self.discount_type == 'percent' else '€'})"

    def is_valid(self) -> bool:
        from django.utils import timezone
        return self.is_active and self.expires_at > timezone.now()
"""Modèles marketing pour newsletter et paniers abandonnés.

Cette version initiale enregistre uniquement les abonnements à la
newsletter. L'envoi d'e‑mails et la relance des paniers
abandonnés seront gérés par des tâches Celery.
"""

from django.db import models


class NewsletterSubscription(models.Model):
    """Adresse e‑mail inscrite à la newsletter."""

    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.email
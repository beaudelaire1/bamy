# notifications/models.py
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class Notification(models.Model):
    """
    Notification interne (affichée dans l'UI) pour un utilisateur.
    Sert à informer des commandes, changements de statut, etc.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        verbose_name = "notification"
        verbose_name_plural = "notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "read"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self) -> str:
        return f"Notification pour {self.user} — {self.message}"

    def mark_as_read(self, commit: bool = True) -> None:
        self.read = True
        if commit:
            self.save(update_fields=["read"])


class EmailNotification(models.Model):
    """
    Notification envoyée par e-mail à un utilisateur.
    Cette table conserve une trace (audit) des e-mails expédiés.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_notifications",
    )
    subject = models.CharField(max_length=255)
    body_text = models.TextField(help_text="Version texte (fallback).")
    body_html = models.TextField(blank=True, default="", help_text="Version HTML (optionnelle).")
    created_at = models.DateTimeField(auto_now_add=True)
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "notification par e-mail"
        verbose_name_plural = "notifications par e-mail"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "sent"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self) -> str:
        return f"EmailNotification pour {self.user} — {self.subject}"

    def mark_as_sent(self, when: timezone.datetime | None = None, commit: bool = True) -> None:
        self.sent = True
        self.sent_at = when or timezone.now()
        if commit:
            self.save(update_fields=["sent", "sent_at"])

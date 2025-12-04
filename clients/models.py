from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Client(models.Model):
    """Represents a B2B customer organisation.

    A client encapsulates company‑wide preferences such as default
    currency, pricing mode and feature flags.  Multiple Django users
    may be linked to a client via the :class:`UserClientLink` model.
    """

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)

    # configuration fields
    settings_currency = models.CharField(
        max_length=10,
        default="EUR",
        help_text=_("Code ISO de la devise par défaut pour ce client."),
    )
    default_pricing_mode = models.CharField(
        max_length=32,
        default="public",
        help_text=_(
            "Mode de tarification par défaut (public, b2b, promotion, etc.)."
        ),
    )
    allowed_features = models.JSONField(
        default=list,
        blank=True,
        help_text=_(
            "Liste de fonctionnalités activées pour ce client (ex: 'quotes', 'promotions')."
        ),
    )
    sales_rep = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="managed_clients",
        help_text=_("Représentant commercial assigné à ce client."),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("client")
        verbose_name_plural = _("clients")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class UserClientLink(models.Model):
    """Associates a Django user with a client using a role.

    Each user can belong to multiple clients, and each client can have
    multiple users.  The ``role`` field defines the level of
    permissions granted to the user for the associated client.
    """

    class Roles(models.TextChoices):
        OWNER = "owner", _("Propriétaire")
        ADMIN = "admin", _("Administrateur")
        MEMBER = "member", _("Membre")
        READ_ONLY = "read_only", _("Lecture seule")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_links",
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="user_links",
    )
    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.MEMBER,
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "client"]
        verbose_name = _("link utilisateur‑client")
        verbose_name_plural = _("liens utilisateur‑client")

    def __str__(self) -> str:
        return f"{self.user} → {self.client} ({self.get_role_display()})"

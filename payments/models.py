"""Modèles pour la gestion des paiements.

Ce module définit la structure de stockage des transactions de paiement. Lorsqu'un
client procède au règlement d'une commande via PayPal, Stripe ou un autre
fournisseur, une instance de :class:`Payment` est créée afin de consigner
les informations essentielles : identifiant du paiement externe, montant,
devise, statut et éventuel lien avec une commande locale. Cela permet de
suivre l'historique des paiements et de vérifier la concordance des
transactions avec les commandes enregistrées.

La table est volontairement minimaliste et peut être enrichie (webhooks,
réconciliation, journalisation des réponses API) en fonction des besoins.
"""

from django.db import models
from django.conf import settings


class Payment(models.Model):
    """Représente un paiement effectué par un utilisateur.

    Chaque paiement est optionnellement associé à une commande (:class:`orders.Order`).
    Le champ :attr:`provider` indique la plateforme utilisée (PayPal, Stripe, etc.).
    Le champ :attr:`transaction_id` stocke l'identifiant unique retourné par
    l'API du prestataire. Le montant et la devise permettent de vérifier la
    cohérence financière. Le statut suit l'état du paiement (en attente,
    complété, échoué). Les dates de création et de mise à jour sont
    automatiquement gérées.
    """

    PROVIDER_CHOICES = [
        ("paypal", "PayPal"),
        ("stripe", "Stripe"),
        ("other", "Autre"),
    ]

    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        help_text="Commande associée à ce paiement, si connue.",
    )
    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        default="other",
        help_text="Prestataire de paiement utilisé.",
    )
    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        help_text="Identifiant retourné par l'API du prestataire.",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Montant du paiement.",
    )
    currency = models.CharField(
        max_length=10,
        default="EUR",
        help_text="Devise du paiement (ISO 4217).",
    )
    status = models.CharField(
        max_length=20,
        default="pending",
        help_text="Statut du paiement (pending, completed, failed).",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.provider}:{self.transaction_id}"  # pragma: no cover

    def mark_completed(self) -> None:
        """Met à jour le statut en 'completed' et sauvegarde l'instance.

        Cette méthode est utile pour centraliser la logique de transition
        d'état lorsqu'un paiement est confirmé par le prestataire. Elle peut
        être appelée par un webhook ou à la suite d'un appel de capture.
        """
        self.status = "completed"
        self.save(update_fields=["status", "updated_at"])

"""Modèles pour les demandes de retour et de remboursement."""

from django.db import models
from django.utils import timezone
from orders.models import OrderItem


class ReturnRequest(models.Model):
    """Représente une demande de retour d'article.

    Chaque demande est attachée à un item de commande et comporte un
    statut indiquant son traitement. Le remboursement réel doit être
    déclenché manuellement en back office ou via l'intégration ERP.
    """

    STATUS_CHOICES = [
        ("pending", "En attente"),
        ("approved", "Approuvée"),
        ("rejected", "Refusée"),
        ("refunded", "Remboursée"),
    ]

    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name="return_requests")
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"Retour {self.order_item} ({self.status})"

    def approve(self) -> None:
        self.status = "approved"
        self.processed_at = timezone.now()
        self.save(update_fields=["status", "processed_at"])

    def reject(self) -> None:
        self.status = "rejected"
        self.processed_at = timezone.now()
        self.save(update_fields=["status", "processed_at"])

    def refund(self) -> None:
        """Marque la demande comme remboursée.

        Dans une version future, ce mécanisme déclenchera le remboursement
        via le fournisseur de paiement ou l'ERP.
        """
        self.status = "refunded"
        self.processed_at = timezone.now()
        self.save(update_fields=["status", "processed_at"])
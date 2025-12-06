from __future__ import annotations

from django.db import models
from core.interfaces import CartRepository, OrderRepository, OrderDTO
from orders.models import Order


class OrderService:
    """
    Service métier pour la création et la consultation des commandes.

    Cette classe sert de façade entre les couches externes (API, vues)
    et l'infrastructure de persistance. Les vues ne manipulent plus
    directement le modèle Django ``Order`` ; elles demandent au service
    un queryset pré-filtré en fonction des paramètres HTTP.
    """

    def __init__(self, cart_repo: CartRepository, order_repo: OrderRepository) -> None:
        self.cart_repo = cart_repo
        self.order_repo = order_repo

    def create_order_from_current_cart(self, request, user_id: int | None) -> OrderDTO:
        cart = self.cart_repo.get_for_request(request)
        if not cart.items:
            raise ValueError("Impossible de créer une commande depuis un panier vide.")
        order = self.order_repo.create_from_cart(cart, user_id=user_id)
        return order

    def get_orders_queryset(
        self,
        *,
        status: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        only_paid: bool = False,
    ):
        """
        Retourne un queryset d'objets ``Order`` filtré selon les critères
        fournis. Cette méthode encapsule toute la logique de filtrage
        utilisée par les vues API (commandes et factures).
        """
        qs = Order.objects.all().prefetch_related("items")
        # Filtre de base : factures uniquement
        if only_paid:
            qs = qs.filter(status="paid")
        # Filtrage par statut spécifique si demandé
        if status:
            qs = qs.filter(status=status)
        # Filtrage par plage de dates (sur la date de création)
        if from_date:
            qs = qs.filter(created_at__date__gte=from_date)
        if to_date:
            qs = qs.filter(created_at__date__lte=to_date)
        return qs.order_by("-created_at")

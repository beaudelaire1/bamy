"""Vues API fournissant des points d'accès REST.

Ces vues utilisent Django REST Framework pour exposer des
serialiseurs, permettant l'intégration avec des systèmes externes
(SAGE X3, Biziipad). Actuellement, seuls les endpoints de
consultation sont implémentés pour les commandes/factures.
"""
from rest_framework import viewsets, permissions
from django.db import models
from rest_framework.generics import ListAPIView

from .serializers import OrderSerializer, InvoiceSerializer, ProductSerializer
from .serializers import QuoteSerializer
from quotes.models import Quote

from core.factory import get_order_service, get_product_service



class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """Endpoint en lecture seule pour les commandes.

    Permet de récupérer la liste des commandes ou le détail d'une
    commande via `/api/orders/` et `/api/orders/{id}/`. Les
    utilisateurs doivent être authentifiés (API token) pour accéder
    à ces données.
    """

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Récupère le queryset des commandes via le service métier.
        
        La vue ne construit plus directement le queryset sur le modèle
        ``Order`` ; elle délègue cette responsabilité à
        ``OrderService`` exposé par la factory centrale.
        """
        service = get_order_service()
        status = self.request.query_params.get("status")
        from_date = self.request.query_params.get("from")
        to_date = self.request.query_params.get("to")
        return service.get_orders_queryset(
            status=status,
            from_date=from_date,
            to_date=to_date,
            only_paid=False,
        )


class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    """Endpoint en lecture seule pour les factures.

    Dans cette version, les factures sont équivalentes aux commandes.
    Cette vue réutilise l'OrderSerializer pour exposer la même
    structure et autorise uniquement la lecture.
    """

    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Récupère le queryset des factures via le service métier.

        Dans cette version, une facture correspond à une commande
        ayant le statut ``paid``. Le filtrage est centralisé dans
        ``OrderService``.
        """
        service = get_order_service()
        status = self.request.query_params.get("status")
        from_date = self.request.query_params.get("from")
        to_date = self.request.query_params.get("to")
        return service.get_orders_queryset(
            status=status,
            from_date=from_date,
            to_date=to_date,
            only_paid=True,
        )


class ProductSearchView(ListAPIView):
    """Endpoint de recherche rapide des produits.

    Permet de rechercher des produits par titre, code article ou EAN.
    La recherche est limitée à 20 résultats et ne nécessite pas
    d'authentification.
    """

    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """
        Délègue la recherche de produits au ``ProductService``.

        La vue ne construit plus directement de requêtes sur le modèle
        ``Product`` ; elle transmet simplement le terme de recherche
        fourni en paramètre de requête.
        """
        service = get_product_service()
        query = self.request.GET.get("q", "").strip()
        return service.search_queryset_for_api(query=query, limit=20)


# -----------------------------------------------------------------------------
# Devis (quotes)
# -----------------------------------------------------------------------------
class QuoteViewSet(viewsets.ModelViewSet):
    """Endpoint CRUD pour les devis.

    Permet de lister, créer et mettre à jour les devis du système.  Les
    utilisateurs doivent être authentifiés.  Lors de la création, les
    items associés sont traités via le sérialiseur.
    """

    serializer_class = QuoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Quote.objects.all().prefetch_related("items__product")
        # Si l'utilisateur n'est pas superuser, on restreint aux devis
        # associés au client via ses liens.  Cette logique de filtrage
        # pourrait être déplacée dans un ``QuerySet`` custom.
        if not user.is_superuser:
            qs = qs.filter(
                models.Q(client__user_links__user=user) | models.Q(user=user)
            ).distinct()
        # Filtrer par statut si nécessaire
        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("-created_at")
"""Vues API fournissant des points d'accès REST.

Ces vues utilisent Django REST Framework pour exposer des
serialiseurs, permettant l'intégration avec des systèmes externes
(SAGE X3, Biziipad). Actuellement, seuls les endpoints de
consultation sont implémentés pour les commandes/factures.
"""

from rest_framework import viewsets, permissions
from orders.models import Order
from .serializers import OrderSerializer, InvoiceSerializer, ProductSerializer
from catalog.models import Product
from django.db.models import Q
from rest_framework.generics import ListAPIView


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
        qs = Order.objects.all().prefetch_related("items")
        # Filtrage par statut
        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status=status)
        # Filtrage par date de création
        from_date = self.request.query_params.get("from")
        to_date = self.request.query_params.get("to")
        if from_date:
            qs = qs.filter(created_at__date__gte=from_date)
        if to_date:
            qs = qs.filter(created_at__date__lte=to_date)
        return qs.order_by("-created_at")


class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    """Endpoint en lecture seule pour les factures.

    Dans cette version, les factures sont équivalentes aux commandes.
    Cette vue réutilise l'OrderSerializer pour exposer la même
    structure et autorise uniquement la lecture.
    """

    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Order.objects.filter(status="paid").prefetch_related("items")
        # Les mêmes paramètres de filtre que pour les commandes
        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status=status)
        from_date = self.request.query_params.get("from")
        to_date = self.request.query_params.get("to")
        if from_date:
            qs = qs.filter(created_at__date__gte=from_date)
        if to_date:
            qs = qs.filter(created_at__date__lte=to_date)
        return qs.order_by("-created_at")


class ProductSearchView(ListAPIView):
    """Endpoint de recherche rapide des produits.

    Permet de rechercher des produits par titre, code article ou EAN.
    La recherche est limitée à 20 résultats et ne nécessite pas
    d'authentification.
    """

    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        qs = Product.objects.filter(is_active=True)
        if query:
            qs = qs.filter(
                Q(title__icontains=query)
                | Q(article_code__icontains=query)
                | Q(ean__icontains=query)
            )
        return qs.order_by("-updated_at")[:20]
"""Routes pour l'API REST.

Ce module définit les endpoints pour les commandes et les factures.
Les routes sont automatiquement générées via un routeur DRF.
"""

from django.urls import include, path
from rest_framework import routers
from .views import OrderViewSet, InvoiceViewSet, ProductSearchView


router = routers.DefaultRouter()
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"invoices", InvoiceViewSet, basename="invoice")


urlpatterns = [
    path("", include(router.urls)),
    # Recherche produit
    path("products/search/", ProductSearchView.as_view(), name="product-search"),
]
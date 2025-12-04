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
router.register(r"quotes", __import__("api.views", fromlist=["QuoteViewSet"]).QuoteViewSet, basename="quote")


urlpatterns = [
    path("", include(router.urls)),
    # Recherche produit
    path("products/search/", ProductSearchView.as_view(), name="product-search"),
]



from django.urls import path, include
from .cart_api import (
    CartDetailAPIView,
    CartAddItemAPIView,
    CartClearAPIView,
    CartCheckoutAPIView,
)
from .auth_api import LoginAPIView, RefreshTokenAPIView

# Routes additionnelles pour le panier et l'authentification JWT
urlpatterns += [
    # Panier
    path("cart/", CartDetailAPIView.as_view(), name="cart-detail-api"),
    path("cart/add/", CartAddItemAPIView.as_view(), name="cart-add-api"),
    path("cart/clear/", CartClearAPIView.as_view(), name="cart-clear-api"),
    path("cart/checkout/", CartCheckoutAPIView.as_view(), name="cart-checkout-api"),
    # Authentification JWT
    path("auth/login/", LoginAPIView.as_view(), name="jwt-login"),
    path("auth/refresh/", RefreshTokenAPIView.as_view(), name="jwt-refresh"),

    # Prévisualisation de prix (endpoint expérimental)
    path(
        "pricing/preview/<int:product_id>/",
        __import__("api.pricing_api", fromlist=["PricingPreviewAPIView"]).PricingPreviewAPIView.as_view(),
        name="pricing-preview",
    ),
]

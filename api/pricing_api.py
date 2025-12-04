"""
Endpoint de prévisualisation des prix.

Ce module expose une vue DRF permettant de simuler le calcul du prix
d'un produit pour une quantité donnée en tenant compte des règles
avancées (quantité, marque, famille, prix plancher).  Il est destiné
aux intégrations externes (ex: front B2B, ERP) qui souhaitent
prévisualiser le prix final sans passer par le processus de commande.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.shortcuts import get_object_or_404

from catalog.models import Product
from core.factory import get_pricing_service


class PricingPreviewAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, product_id: int):
        """Retourne le prix unitaire d'un produit pour une quantité donnée.

        L'endpoint attend un paramètre ``quantity`` dans la chaîne de
        requête.  S'il n'est pas fourni ou invalide, la valeur 1 est
        utilisée par défaut.
        """
        try:
            quantity = int(request.query_params.get("quantity", 1))
        except Exception:
            quantity = 1
        product = get_object_or_404(Product, pk=product_id)
        pricing_service = get_pricing_service()
        unit_price = pricing_service.preview_price(product, request.user, quantity)
        return Response(
            {
                "product_id": product.id,
                "quantity": quantity,
                "unit_price": unit_price,
            }
        )

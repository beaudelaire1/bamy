from __future__ import annotations

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from core.factory import get_cart_service, get_order_service


class CartDetailAPIView(APIView):
    """
    Retourne le contenu du panier courant pour l'utilisateur authentifié.

    Cette vue est un simple adaptateur HTTP -> service de domaine.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        service = get_cart_service()
        cart = service.get_cart(request)
        data = {
            "total": str(cart.total or 0),
            "items": [
                {
                    "product_id": it.product.id,
                    "sku": it.product.sku,
                    "quantity": it.quantity,
                    "unit_price": str(it.unit_price) if it.unit_price is not None else None,
                    "total_price": str(it.total_price) if it.total_price is not None else None,
                }
                for it in cart.items
            ],
        }
        return Response(data)


class CartAddItemAPIView(APIView):
    """
    Ajoute un article au panier à partir d'un SKU et d'une quantité.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        sku = request.data.get("sku")
        qty = int(request.data.get("quantity", 1))
        client_type = getattr(getattr(request.user, "profile", None), "client_type", None)
        service = get_cart_service()
        cart = service.add_item(request, sku=sku, quantity=qty, client_type=client_type)
        return Response(
            {"total": str(cart.total or 0)},
            status=status.HTTP_200_OK,
        )


class CartClearAPIView(APIView):
    """
    Vide entièrement le panier courant.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        service = get_cart_service()
        cart = service.clear(request)
        return Response({"total": str(cart.total or 0), "items": []})


class CartCheckoutAPIView(APIView):
    """
    Crée une commande à partir du panier courant.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        service = get_order_service()
        user_id = request.user.id if request.user.is_authenticated else None
        order = service.create_order_from_current_cart(request, user_id=user_id)
        return Response(
            {
                "id": order.id,
                "order_number": order.order_number,
                "total": str(order.total),
                "status": order.status,
            },
            status=status.HTTP_201_CREATED,
        )

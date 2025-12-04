"""Sérialiseurs pour les points d'entrée REST.

Cette application expose des API destinées à l'intégration avec des
outils externes (SAGE X3, Biziipad). Les sérialiseurs définissent
comment nos modèles sont représentés en JSON.
"""

from rest_framework import serializers
from orders.models import Order, OrderItem
from catalog.models import Product
from core.factory import get_pricing_service


class OrderItemSerializer(serializers.ModelSerializer):
    """Sérialiseur des lignes de commande."""

    class Meta:
        model = OrderItem
        fields = [
            "product_title",
            "product_sku",
            "unit_price",
            "quantity",
            "line_total",
        ]


class OrderSerializer(serializers.ModelSerializer):
    """Sérialiseur de commande.

    Ce sérialiseur expose les informations pertinentes d'une commande,
    y compris les coordonnées client, les totaux et les lignes de
    commande. C'est ce format qui sera consommé par les API
    externes afin de récupérer les factures.
    """

    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        # On expose explicitement les champs utiles
        fields = [
            "id",
            "order_number",
            "status",
            "created_at",
            "email",
            "first_name",
            "last_name",
            "phone",
            "company",
            "address1",
            "address2",
            "city",
            "postcode",
            "country",
            "subtotal",
            "shipping",
            "total",
            "items",
        ]


class InvoiceSerializer(OrderSerializer):
    """Alias pour OrderSerializer.

    Dans cette version, les factures sont dérivées des commandes. Si un
    modèle distinct de Facture est introduit plus tard, ce
    sérialiseur pourra être adapté.
    """

    class Meta(OrderSerializer.Meta):
        pass


class ProductSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les produits avec prix final calculé."""

    final_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "article_code",
            "price",
            "discount_price",
            "final_price",
        ]

    def get_final_price(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None) if request is not None else None
        pricing_service = get_pricing_service()
        return pricing_service.get_unit_price(obj, user)

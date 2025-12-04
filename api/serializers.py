"""Sérialiseurs pour les points d'entrée REST.

Cette application expose des API destinées à l'intégration avec des
outils externes (SAGE X3, Biziipad). Les sérialiseurs définissent
comment nos modèles sont représentés en JSON.
"""

from rest_framework import serializers
from orders.models import Order, OrderItem
from quotes.models import Quote, QuoteItem
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


# -----------------------------------------------------------------------------
# Devis (quotes)
# -----------------------------------------------------------------------------
class QuoteItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteItem
        fields = ["product", "product_title", "product_sku", "unit_price", "quantity", "line_total"]

    product_title = serializers.CharField(source="product.title", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)


class QuoteSerializer(serializers.ModelSerializer):
    items = QuoteItemSerializer(many=True)

    class Meta:
        model = Quote
        fields = ["id", "client", "user", "status", "notes", "created_at", "validated_at", "subtotal", "items"]
        read_only_fields = ["id", "created_at", "validated_at", "subtotal"]

    def create(self, validated_data):
        # Détacher les items du payload
        items_data = validated_data.pop("items", [])
        quote = Quote.objects.create(**validated_data)
        # Crée chaque item et calcule le prix final via le service de pricing
        from core.factory import get_pricing_service
        pricing_service = get_pricing_service()
        user = quote.user
        for item_data in items_data:
            product = item_data["product"]
            quantity = item_data.get("quantity", 1)
            unit_price = pricing_service.preview_price(product, user, quantity)
            QuoteItem.objects.create(
                quote=quote,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                line_total=(unit_price * quantity),
            )
        return quote

from decimal import Decimal
from django.http import JsonResponse, HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from cart.cart import Cart
from orders.models import Order
from .models import Payment
from .paypal import create_order, capture_order
from .stripe_api import create_checkout_session

def _total_str(cart: Cart) -> str:
    total = getattr(cart, "total", Decimal("0"))
    return f"{Decimal(total):.2f}"

@require_POST
def paypal_create(request: HttpRequest):
    cart = Cart(request)
    data = create_order(_total_str(cart))
    return JsonResponse({"id": data.get("id")})

@require_POST
def paypal_capture(request: HttpRequest):
    oid = request.POST.get("orderID")
    if not oid:
        return JsonResponse({"ok": False, "error":"orderID manquant"}, status=400)
    data = capture_order(oid)
    # Une fois la commande PayPal capturée, on tente de marquer la commande locale comme payée.
    # Le numéro de commande local peut être transmis via le champ "order_number" du POST.
    order_number = request.POST.get("order_number")
    if order_number:
        try:
            order = Order.objects.get(order_number=order_number)
            # Met à jour le statut de la commande locale
            order.status = "paid"
            order.save(update_fields=["status"])
            # Crée un enregistrement de paiement associé
            Payment.objects.create(
                order=order,
                provider="paypal",
                transaction_id=oid,
                amount=order.total,
                currency="EUR",
                status="completed",
            )
        except Order.DoesNotExist:
            pass
    return JsonResponse({"ok": True, "data": data})

@require_POST
def stripe_checkout(request: HttpRequest):
    cart = Cart(request)
    cents = int(Decimal(_total_str(cart)) * 100)
    success = request.build_absolute_uri(reverse("cart:detail"))  # remplace par orders:success si dispo
    cancel  = request.build_absolute_uri(reverse("cart:detail"))
    session = create_checkout_session(cents, success, cancel)
    return redirect(session.url)

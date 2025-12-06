from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils import timezone

from cart.cart import Cart
from core.signals import order_validated
from core.factory import get_cart_service  # importe le service de panier
from .forms import CheckoutForm
from .models import Order, OrderItem

try:
    from loyalty.models import Coupon  # type: ignore
except Exception:
    Coupon = None

User = get_user_model()

def checkout(request):
    # On récupère le panier brut stocké en session et le convertit en DTO
    # via le service de panier afin de disposer des prix calculés.  Le
    # service applique les promotions et les tarifs B2B ; aucun calcul
    # de prix ne doit être effectué dans cette vue.
    cart_session = Cart(request)
    if len(cart_session) == 0:
        messages.info(request, "Votre panier est vide.")
        return redirect("cart:detail")
    cart_service = get_cart_service()
    cart_dto = cart_service.get_cart(request)

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                data = form.cleaned_data
                # Calcul du total et éventuelle remise via coupon en se basant
                # sur le panier tarifé.  Le total TTC du panier est
                # ``cart_dto.total`` ; on n'utilise plus ``cart.total`` qui n'est
                # plus calculé dans l'objet session.
                coupon_code = request.session.get("coupon_code") if Coupon else None
                discount_amount = 0
                if coupon_code and Coupon:
                    try:
                        coupon = Coupon.objects.get(code__iexact=coupon_code, is_active=True)
                        # Si le coupon est valide et non expiré
                        if coupon.expires_at > timezone.now():
                            base_total = cart_dto.total or 0
                            if coupon.discount_type == "percent":
                                discount_amount = (base_total * coupon.discount_value) / 100
                            else:
                                discount_amount = coupon.discount_value
                            if discount_amount > base_total:
                                discount_amount = base_total
                    except Coupon.DoesNotExist:
                        discount_amount = 0

                subtotal = cart_dto.total or 0
                total = subtotal - discount_amount

                order = Order.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    email=data["email"],
                    first_name=data["first_name"],
                    last_name=data["last_name"],
                    phone=data.get("phone", ""),
                    company=data.get("company", ""),
                    address1=data["address1"],
                    address2=data.get("address2", ""),
                    city=data["city"],
                    postcode=data["postcode"],
                    country=data["country"],
                    notes=data.get("notes", ""),
                    subtotal=subtotal,
                    shipping=0,
                    total=total,
                    coupon_code=coupon_code or "",
                    discount=discount_amount,
                )

                # Lignes de commande : on utilise les items tarifés du CartDTO
                for item_dto in cart_dto.items:
                    OrderItem.objects.create(
                        order=order,
                        product_title=getattr(item_dto.product, "title", ""),
                        product_sku=item_dto.product.sku,
                        unit_price=item_dto.unit_price,
                        quantity=item_dto.quantity,
                        line_total=item_dto.total_price,
                    )

                # Nettoyage panier (session)
                cart_session.clear()
                # Supprime le coupon utilisé de la session pour éviter une réutilisation
                request.session.pop("coupon_code", None)

                # Création d'une notification interne pour l'utilisateur connecté
                if request.user.is_authenticated:
                    try:
                        from notifications.models import Notification  # import local pour éviter dépendance circulaire
                        Notification.objects.create(
                            user=request.user,
                            message=f"Votre commande {order.order_number} a été créée."
                        )
                    except Exception:
                        # Laisse passer silencieusement si l'app notifications n'est pas installée
                        pass
                    # Émet un signal pour permettre à des applications tierces
                    # (par exemple loyalty) de réagir à la validation d'une commande
                    try:
                        order_validated.send(sender=Order, order=order, user=request.user)
                    except Exception:
                        # Si l'émetteur échoue on n'empêche pas la commande de se créer
                        pass

                # Envoi d'un email interne pour signaler la création d'une commande
                try:
                    from django.conf import settings
                    from django.core.mail import send_mail
                    internal_subject = f"[COMMANDE] Nouvelle commande {order.order_number}"
                    internal_body = (
                        f"Une nouvelle commande vient d'être passée.\n\n"
                        f"Numéro de commande : {order.order_number}\n"
                        f"Client : {order.first_name} {order.last_name} ({order.email})\n"
                        f"Date : {order.created_at}\n"
                        f"Total TTC : {order.total} €\n\n"
                        "Consultez l'administration pour plus de détails."
                    )
                    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or None
                    send_mail(internal_subject, internal_body, from_email, getattr(settings, "INTERNAL_CONTACTS", []))
                    # Envoi d'un email de confirmation au client
                    company_name = getattr(settings, "COMPANY_NAME", "Notre boutique")
                    client_subject = f"Votre commande {order.order_number} chez {company_name}"
                    client_body = (
                        "Bonjour,\n\n"
                        "Nous vous remercions pour votre commande. Voici un récapitulatif :\n\n"
                        f"Numéro de commande : {order.order_number}\n"
                        f"Total TTC : {order.total} €\n\n"
                        "Nous préparerons votre commande dans les meilleurs délais.\n\n"
                        f"Cordialement,\nL'équipe {company_name}"
                    )
                    send_mail(client_subject, client_body, from_email, [order.email])
                except Exception:
                    # Ignore les erreurs d'envoi en développement
                    pass

            messages.success(request, "Commande créée avec succès.")
            return redirect("orders:success", order_number=order.order_number)
        else:
            messages.error(request, "Merci de corriger les erreurs.")
    else:
        # Préremplir si utilisateur connecté
        initial = {}
        if request.user.is_authenticated:
            u = request.user
            initial = {
                "email": getattr(u, "email", ""),
                "first_name": getattr(u, "first_name", ""),
                "last_name": getattr(u, "last_name", ""),
                "company": getattr(u, "company_name", ""),
            }
        # Si l'utilisateur possède une adresse par défaut, préremplir les champs
        if request.user.is_authenticated:
            try:
                from userauths.models import Address
                default_addr = Address.objects.filter(user=request.user, is_default=True).first()
                if default_addr:
                    initial.update({
                        "address1": getattr(default_addr, "address1", ""),
                        "address2": getattr(default_addr, "address2", ""),
                        "city": default_addr.city,
                        "postcode": default_addr.postcode,
                        "country": default_addr.country,
                        "phone": default_addr.phone,
                    })
            except Exception:
                pass
        form = CheckoutForm(initial=initial)

    # Pour l'affichage dans la page de checkout, on reconstruit un
    # objet panier « vue » similaire à celui utilisé dans cart/views.py.
    # Cela permet aux templates existants de continuer à itérer sur
    # ``cart`` et d'accéder aux champs ``price``, ``unit_price`` et
    # ``total_price``.  On fusionne les lignes brutes du panier (issues de
    # la session) avec les prix calculés (issus du service de panier).
    from decimal import Decimal
    priced_map = {ci.product.id: ci for ci in cart_dto.items}
    view_items = []
    for entry in cart_session:
        pid = entry["product_id"]
        product = entry["product"]
        qty = entry["quantity"]
        priced = priced_map.get(pid)
        unit_price = getattr(priced, "unit_price", None)
        line_total = getattr(priced, "total_price", None)
        view_items.append({
            "product": product,
            "product_id": pid,
            "quantity": qty,
            "qty": qty,
            "price": unit_price,
            "unit_price": unit_price,
            "total_price": line_total,
            "total": line_total,
        })

    class ViewCart:
        def __init__(self, items, total):
            self._items = items
            self.total = total

        def __iter__(self):
            return iter(self._items)

        def __len__(self):
            return len(self._items)

        def items(self):  # pragma: no cover
            return list(self._items)

    view_cart = ViewCart(view_items, cart_dto.total or Decimal("0"))

    return render(
        request,
        "orders/checkout.html",
        {
            "cart": view_cart,
            "form": form,
        },
    )

def checkout_success(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number)
    except Order.DoesNotExist:
        messages.error(request, "Commande introuvable.")
        return redirect("core:home")
    return render(request, "orders/success.html", {"order": order})

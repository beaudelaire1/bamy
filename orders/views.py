from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils import timezone

from cart.cart import Cart
from .forms import CheckoutForm
from .models import Order, OrderItem

try:
    from loyalty.models import Coupon  # type: ignore
except Exception:
    Coupon = None

User = get_user_model()

def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.info(request, "Votre panier est vide.")
        return redirect("cart:detail")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                data = form.cleaned_data
                # Calcul du total et éventuelle remise via coupon
                coupon_code = request.session.get("coupon_code") if Coupon else None
                discount_amount = 0
                if coupon_code and Coupon:
                    try:
                        coupon = Coupon.objects.get(code__iexact=coupon_code, is_active=True)
                        # Si le coupon est valide et non expiré
                        if coupon.expires_at > timezone.now():
                            if coupon.discount_type == "percent":
                                discount_amount = (cart.total * coupon.discount_value) / 100
                            else:
                                discount_amount = coupon.discount_value
                            if discount_amount > cart.total:
                                discount_amount = cart.total
                    except Coupon.DoesNotExist:
                        discount_amount = 0

                subtotal = cart.total
                total = subtotal - discount_amount

                order = Order.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    email=data["email"],
                    first_name=data["first_name"],
                    last_name=data["last_name"],
                    phone=data.get("phone",""),
                    company=data.get("company",""),
                    address1=data["address1"],
                    address2=data.get("address2",""),
                    city=data["city"],
                    postcode=data["postcode"],
                    country=data["country"],
                    notes=data.get("notes",""),
                    subtotal=subtotal,
                    shipping=0,
                    total=total,
                    coupon_code=coupon_code or "",
                    discount=discount_amount,
                )

                # Lignes
                for item in cart:
                    OrderItem.objects.create(
                        order=order,
                        product_title=item["product"].title,
                        product_sku=item["product"].sku,
                        unit_price=item["price"],
                        quantity=item["quantity"],
                        line_total=item["total_price"],
                    )

                # Nettoyage panier
                cart.clear()
                # Supprime le coupon utilisé de la session pour éviter une réutilisation
                request.session.pop("coupon_code", None)

                # Création d'une notification et attribution de points fidélité à l'utilisateur connecté
                if request.user.is_authenticated:
                    # Notification interne (si l'application notifications est présente)
                    try:
                        from notifications.models import Notification  # import local pour éviter dépendance circulaire
                        Notification.objects.create(
                            user=request.user,
                            message=f"Votre commande {order.order_number} a été créée."
                        )
                    except Exception:
                        # Laisse passer silencieusement si l'app notifications n'est pas installée
                        pass

                    # Ajout de points de fidélité : 1 point par euro dépensé (hors centimes)
                    try:
                        from loyalty.models import LoyaltyAccount
                        account, _ = LoyaltyAccount.objects.get_or_create(user=request.user)
                        # On attribue des points équivalents à la partie entière du total
                        account.points = account.points + int(order.total)
                        account.save(update_fields=["points"])
                    except Exception:
                        # Ignore si l'app loyalty n'est pas installée
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

    return render(request, "orders/checkout.html", {"cart": cart, "form": form})

def checkout_success(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number)
    except Order.DoesNotExist:
        messages.error(request, "Commande introuvable.")
        return redirect("core:home")
    return render(request, "orders/success.html", {"order": order})

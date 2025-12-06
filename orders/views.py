from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import get_user_model

from cart.cart import Cart
from core.signals import order_validated
from core.factory import get_cart_service  # fabrique du service de panier

from .forms import CheckoutForm
from .models import Order
from .services import CheckoutService

User = get_user_model()


def checkout(request):
    """Vue de checkout HTTP.

    La logique métier (calcul des montants, application du coupon,
    création de la commande et des lignes) est entièrement déléguée au
    ``CheckoutService`` d'``orders.services``.  La vue se limite à :

    * vérifier que le panier n'est pas vide ;
    * gérer les formulaires et messages ;
    * orchestrer les notifications et les emails ;
    * préparer les données de présentation pour le template.
    """

    # Panier brut (session) pour contrôle rapide
    cart_session = Cart(request)
    if len(cart_session) == 0:
        messages.info(request, "Votre panier est vide.")
        return redirect("cart:detail")

    # Panier enrichi via le service de domaine (prix calculés)
    cart_service = get_cart_service()
    cart_dto = cart_service.get_cart(request)
    checkout_service = CheckoutService(cart_service=cart_service)

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                order = checkout_service.checkout(request, form)
            except ValueError:
                messages.info(request, "Votre panier est vide.")
                return redirect("cart:detail")

            # Création d'une notification interne pour l'utilisateur connecté
            if request.user.is_authenticated:
                try:
                    # Import local pour éviter les dépendances circulaires
                    from notifications.models import Notification  # type: ignore

                    Notification.objects.create(
                        user=request.user,
                        message=f"Votre commande {order.order_number} a été créée.",
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

            # Envoi d'emails (interne + confirmation client)
            try:
                from django.conf import settings
                from core.utils.async_email import async_send_mail

                internal_subject = f"[COMMANDE] Nouvelle commande {order.order_number}"
                internal_body = (
                    "Une nouvelle commande vient d'être passée.\n\n"
                    f"Numéro de commande : {order.order_number}\n"
                    f"Client : {order.first_name} {order.last_name} ({order.email})\n"
                    f"Date : {order.created_at}\n"
                    f"Total TTC : {order.total} €\n\n"
                    "Consultez l'administration pour plus de détails."
                )
                from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or None
                async_send_mail(
                    internal_subject,
                    internal_body,
                    from_email,
                    getattr(settings, "INTERNAL_CONTACTS", []),
                )

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
                async_send_mail(client_subject, client_body, from_email, [order.email])
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
                    initial.update(
                        {
                            "address1": getattr(default_addr, "address1", ""),
                            "address2": getattr(default_addr, "address2", ""),
                            "city": default_addr.city,
                            "postcode": default_addr.postcode,
                            "country": default_addr.country,
                            "phone": default_addr.phone,
                        }
                    )
            except Exception:
                pass
        form = CheckoutForm(initial=initial)

    # Pour l'affichage dans la page de checkout, on reconstruit un
    # objet panier « vue » similaire à celui utilisé dans cart/views.py.
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
        view_items.append(
            {
                "product": product,
                "product_id": pid,
                "quantity": qty,
                "qty": qty,
                "price": unit_price,
                "unit_price": unit_price,
                "total_price": line_total,
                "total": line_total,
            }
        )

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


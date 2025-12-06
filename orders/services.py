"""Services applicatifs pour l'application ``orders``.

Ces services orchestrent la logique de commande en s'appuyant sur les
services de domaine exposés par ``core`` (panier, pricing) et sur les
modèles Django de l'application.  L'objectif est de sortir la logique
métiers des vues HTTP afin que celles-ci ne fassent plus que :

* récupérer / valider les données de la requête,
* appeler un service,
* gérer les effets de bord d'interface (messages, redirections, rendu).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Tuple, Optional, Any

from django.db import transaction
from django.utils import timezone

from cart.cart import Cart
from core.factory import get_cart_service

from .forms import CheckoutForm
from .models import Order, OrderItem

try:  # Coupon est optionnel (feature loyalty)
    from loyalty.models import Coupon  # type: ignore
except Exception:  # pragma: no cover - absence d'app loyalty
    Coupon = None


class CheckoutService:
    """Service applicatif pour le passage de commande web.

    Ce service encapsule **toute la logique métier financière** liée au
    checkout :

    * récupération du panier tarifé via le ``CartService`` de ``core``,
    * application des coupons (montant ou pourcentage),
    * calcul du sous‑total, de la remise et du total,
    * création de l'``Order`` et des ``OrderItem`` associés,
    * nettoyage du panier et du coupon en session.

    Les vues n'ont plus à manipuler directement les montants ni à
    connaître les règles métier : elles délèguent à ce service et se
    concentrent sur l'IHM (messages, redirections, notifications).
    """

    def __init__(self, cart_service=None) -> None:
        self.cart_service = cart_service or get_cart_service()

    def compute_coupon_discount(self, subtotal: Decimal, request) -> Tuple[Decimal, str, Optional[Any]]:
        """Calcule le montant de remise associé à un éventuel coupon.

        Retourne un tuple ``(discount_amount, coupon_code, coupon_obj)``.
        Si aucun coupon valide n'est présent, la remise vaut 0, le code
        est une chaîne vide et l'objet coupon est ``None``.  Les coupons
        invalides ou expirés sont nettoyés de la session.
        """

        if not Coupon:
            return Decimal("0"), "", None

        coupon_code = request.session.get("coupon_code")
        if not coupon_code:
            return Decimal("0"), "", None

        try:
            coupon = Coupon.objects.get(code__iexact=coupon_code, is_active=True)
        except Coupon.DoesNotExist:
            request.session.pop("coupon_code", None)
            return Decimal("0"), "", None

        # Vérifie la date d'expiration
        if coupon.expires_at and coupon.expires_at <= timezone.now():
            request.session.pop("coupon_code", None)
            return Decimal("0"), "", None

        discount_amount = Decimal("0")
        if coupon.discount_type == "percent":
            discount_amount = (subtotal * coupon.discount_value) / Decimal("100")
        else:
            discount_amount = coupon.discount_value

        if discount_amount > subtotal:
            discount_amount = subtotal

        return discount_amount, coupon.code, coupon

    @transaction.atomic
    def checkout(self, request, form: CheckoutForm) -> Order:
        """Crée une commande à partir du panier courant.

        Lève ``ValueError`` si le panier est vide.
        """

        # Panier brut (session) pour conserver l'interface utilisée par
        # le reste du projet et permettre le nettoyage.
        cart_session = Cart(request)
        if len(cart_session) == 0:
            raise ValueError("Impossible de créer une commande depuis un panier vide.")

        # Panier enrichi via le service de domaine (prix calculés).
        cart_dto = self.cart_service.get_cart(request)
        subtotal = cart_dto.total or Decimal("0")

        # Application éventuelle d'un coupon
        discount_amount, coupon_code, _ = self.compute_coupon_discount(subtotal, request)
        total = subtotal - discount_amount

        data = form.cleaned_data

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
            shipping=Decimal("0"),
            total=total,
            coupon_code=coupon_code or "",
            discount=discount_amount,
        )

        # Création des lignes de commande à partir des items tarifés
        for item_dto in cart_dto.items:
            OrderItem.objects.create(
                order=order,
                product_title=getattr(item_dto.product, "title", ""),
                product_sku=item_dto.product.sku,
                unit_price=item_dto.unit_price,
                quantity=item_dto.quantity,
                line_total=item_dto.total_price,
            )

        # Nettoyage du panier et du coupon en session
        cart_session.clear()
        request.session.pop("coupon_code", None)

        return order


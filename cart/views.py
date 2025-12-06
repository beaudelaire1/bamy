from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.urls import reverse
from catalog.models import Product
from .cart import Cart
from core.factory import get_cart_service
from decimal import Decimal
from django.utils import timezone

# Evitez les doublons d'import : messages et reverse sont importés une seule fois ci-dessus.
try:
    from loyalty.models import Coupon  # type: ignore
except Exception:
    Coupon = None  # fallback when loyalty app is not installed

def detail(request):
    # Utilise le service de panier pour obtenir un panier enrichi
    service = get_cart_service()
    cart_dto = service.get_cart(request)

    # Reconstruit un objet cart pour l'affichage afin de conserver
    # l'interface attendue par les templates (``for item in cart``)
    original_cart = Cart(request)
    # Crée une correspondance entre id de produit et ligne tarifée
    priced_map: dict[int, object] = {ci.product.id: ci for ci in cart_dto.items}
    view_items = []
    for entry in original_cart:
        pid = entry["product_id"]
        priced = priced_map.get(pid)
        # Produit ORM pour l'affichage
        product = entry["product"]
        qty = entry["quantity"]
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

        # Pour compatibilité avec des appels éventuels
        def items(self):
            return list(self._items)

    view_cart = ViewCart(view_items, cart_dto.total or Decimal("0"))

    # Gestion du coupon appliqué (stocké en session)
    coupon_code = request.session.get("coupon_code")
    discount_amount: Decimal = Decimal("0")
    coupon_obj = None
    total_after_discount = view_cart.total
    if coupon_code and Coupon:
        try:
            coupon = Coupon.objects.get(code__iexact=coupon_code, is_active=True)
            # Vérifie expiration
            if coupon.expires_at > timezone.now():
                coupon_obj = coupon
                base_total = view_cart.total
                if coupon.discount_type == "percent":
                    discount_amount = (base_total * coupon.discount_value) / 100
                else:
                    discount_amount = coupon.discount_value
                # Évite un total négatif
                if discount_amount > base_total:
                    discount_amount = base_total
                total_after_discount = base_total - discount_amount
            else:
                # Coupon expiré : on le supprime de la session
                request.session.pop("coupon_code", None)
        except Coupon.DoesNotExist:
            # Coupon inexistant : on nettoie la session
            request.session.pop("coupon_code", None)
    context = {
        "cart": view_cart,
        "cart_count": len(view_cart),
        "coupon_obj": coupon_obj,
        "discount_amount": discount_amount,
        "total_after_discount": total_after_discount,
        "coupon_code": coupon_code,
    }
    return render(request, "cart/detail.html", context)

@require_POST
def apply_coupon(request):
    """Applique un code promo au panier en le stockant dans la session."""
    if Coupon is None:
        messages.error(request, "Aucune fonctionnalité de coupon n'est disponible.")
        return redirect(reverse("cart:detail"))
    code = request.POST.get("coupon_code", "").strip()
    if not code:
        messages.error(request, "Veuillez saisir un code promo.")
        return redirect(reverse("cart:detail"))
    try:
        coupon = Coupon.objects.get(code__iexact=code, is_active=True)
        if coupon.expires_at <= timezone.now():
            raise Coupon.DoesNotExist
        request.session["coupon_code"] = coupon.code
        messages.success(request, f"Le code promo '{coupon.code}' a été appliqué.")
    except Coupon.DoesNotExist:
        request.session.pop("coupon_code", None)
        messages.error(request, "Code promo invalide ou expiré.")
    return redirect(reverse("cart:detail"))

@require_POST
def add(request, product_id):
    # Délègue l'ajout au service de panier afin de recalculer les prix
    qty_str = request.POST.get("qty") or request.POST.get("quantity") or "1"
    try:
        qty_int = int(qty_str)
    except Exception:
        qty_int = 1
    override = request.POST.get("override") in ("1", "true", "True", "on")
    # Si override est utilisé, on mettra à jour la quantité via le Cart directement
    if override:
        cart = Cart(request)
        cart.update(product_id, qty_int)
    else:
        service = get_cart_service()
        # Obtient le SKU depuis le modèle pour utiliser le service
        product = get_object_or_404(Product, id=product_id)
        sku = getattr(product, "article_code", None) or getattr(product, "sku", None)
        service.add_item(request, sku=sku, quantity=qty_int)
    messages.success(request, "Produit ajouté au panier.")
    return redirect(request.POST.get("next") or reverse("cart:detail"))

@require_POST
def update(request, product_id):
    # Met à jour directement la session puis recalcule les prix via le service
    try:
        qty = int(request.POST.get("qty") or request.POST.get("quantity") or 1)
    except Exception:
        qty = 1
    cart = Cart(request)
    cart.update(product_id=product_id, qty=qty)
    messages.info(request, "Quantité mise à jour.")
    return redirect(request.POST.get("next") or reverse("cart:detail"))

@require_POST
def remove(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)
    messages.warning(request, "Produit retiré du panier.")
    return redirect(request.POST.get("next") or reverse("cart:detail"))

@require_POST
def clear(request):
    cart = Cart(request)
    cart.clear()
    messages.info(request, "Panier vidé.")
    return redirect(reverse("cart:detail"))

@require_POST
def add_legacy(request, product_id):
    """
    Compatibilité pour les anciennes URL / cart/add-legacy/<id>/.
    Redirige vers l’ajout normal.
    """
    return add(request, product_id)

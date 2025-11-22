from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.urls import reverse
from catalog.models import Product
from .cart import Cart
from django.utils import timezone

# Evitez les doublons d'import : messages et reverse sont importés une seule fois ci-dessus.
try:
    from loyalty.models import Coupon  # type: ignore
except Exception:
    Coupon = None  # fallback when loyalty app is not installed

def detail(request):
    print(request.user)
    cart = Cart(request)
    # Gestion du coupon appliqué (stocké en session)
    coupon_code = request.session.get("coupon_code")
    discount_amount = 0
    coupon_obj = None
    total_after_discount = cart.total
    if coupon_code and Coupon:
        try:
            coupon = Coupon.objects.get(code__iexact=coupon_code, is_active=True)
            # Vérifie expiration
            if coupon.expires_at > timezone.now():
                coupon_obj = coupon
                if coupon.discount_type == "percent":
                    discount_amount = (cart.total * coupon.discount_value) / 100
                else:
                    discount_amount = coupon.discount_value
                # Évite un total négatif
                if discount_amount > cart.total:
                    discount_amount = cart.total
                total_after_discount = cart.total - discount_amount
            else:
                # Coupon expiré : on le supprime de la session
                request.session.pop("coupon_code", None)
        except Coupon.DoesNotExist:
            # Coupon inexistant : on nettoie la session
            request.session.pop("coupon_code", None)
    context = {
        "cart": cart,
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
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    qty = request.POST.get("qty") or request.POST.get("quantity") or 1
    override = request.POST.get("override") in ("1", "true", "True", "on")
    cart.add(product=product, qty=int(qty), override=override)
    messages.success(request, "Produit ajouté au panier.")
    return redirect(request.POST.get("next") or reverse("cart:detail"))

@require_POST
def update(request, product_id):
    cart = Cart(request)
    qty = int(request.POST.get("qty") or request.POST.get("quantity") or 1)
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

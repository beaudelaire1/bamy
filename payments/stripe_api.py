import os
import stripe
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

def _get_secret_key() -> str:
    # 1) settings (via local_settings.py), 2) variables d'environnement
    key = getattr(settings, "STRIPE_SECRET_KEY", "") or os.getenv("STRIPE_SECRET_KEY", "")
    return (key or "").strip()

def _set_api_key():
    key = _get_secret_key()
    # garde-fous utiles
    if not key:
        raise ImproperlyConfigured(
            "STRIPE_SECRET_KEY manquante. Définis-la dans local_settings.py (ou variable d'env)."
        )
    if key.startswith("pk_"):
        raise ImproperlyConfigured(
            "STRIPE_SECRET_KEY invalide: tu as mis une clé 'pk_...' (publishable). "
            "Utilise la clé secrète 'sk_test_...'."
        )
    if not key.startswith("sk_"):
        raise ImproperlyConfigured(
            "STRIPE_SECRET_KEY invalide: elle doit commencer par 'sk_'."
        )
    stripe.api_key = key

def create_checkout_session(amount_cents: int, success_url: str, cancel_url: str):
    _set_api_key()
    return stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "eur",
                "product_data": {"name": "Commande"},
                "unit_amount": amount_cents,
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )

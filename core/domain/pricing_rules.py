from decimal import Decimal
from typing import Optional


class B2BPricingRules:
    """Règles de tarification B2B.

    Cette classe applique la grille tarifaire en fonction du ``client_type``
    et de l'état de vérification du compte B2B.

    - wholesaler   -> price_wholesaler
    - big_retail   -> price_big_retail
    - small_retail -> price_small_retail

    Si le tarif dédié n'est pas renseigné, on retombe sur ``product.price``.

    Pour les comptes B2B non vérifiés, une surcharge de +5% est appliquée
    sur le prix calculé.

    Pour les clients "public" / "regular" ou en l'absence d'utilisateur,
    cette méthode renvoie ``None`` afin de laisser la main aux autres
    stratégies (promo simple, prix public).
    """

    @staticmethod
    def apply(user, product) -> Optional[Decimal]:
        if user is None:
            return None

        client_type = getattr(user, "client_type", None)
        if client_type not in {"wholesaler", "big_retail", "small_retail"}:
            # Pas de grille B2B pour ce type de client.
            return None

        if client_type == "wholesaler":
            base = product.price_wholesaler or product.price
        elif client_type == "big_retail":
            base = product.price_big_retail or product.price
        else:  # small_retail
            base = getattr(product, "price_small_retail", None) or product.price

        price = Decimal(base)

        # Surcharge compte non vérifié : +5% sur le prix B2B.
        if not getattr(user, "is_b2b_verified", False):
            price = (price * Decimal("1.05")).quantize(Decimal("0.01"))

        return price

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, Iterator, Optional
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils.functional import cached_property
from django.apps import apps


# Paramètres configurables via settings.py
CART_SESSION_ID: str = getattr(settings, "CART_SESSION_ID", "cart")
MIN_QTY: int = int(getattr(settings, "CART_MIN_QTY", 10))  # quantité minimale par défaut (B2B)
PRODUCT_MODEL: str = getattr(settings, "CART_PRODUCT_MODEL", "catalog.Product")

def get_product_model():
    """Récupère dynamiquement le modèle produit configuré."""
    try:
        app_label, model_name = PRODUCT_MODEL.split(".")
        return apps.get_model(app_label, model_name)
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(f"Modèle produit introuvable: {PRODUCT_MODEL}") from exc

Product = get_product_model()

def _to_decimal(val: Any, default: str = "0.00") -> Decimal:
    """Convertit une valeur en Decimal de manière robuste."""
    try:
        return Decimal(str(val))
    except Exception:
        try:
            return Decimal(default)
        except Exception:
            return Decimal("0.00")

def _unit_price_of(product: Any) -> Decimal:
    """
    Détermine le prix unitaire d'un produit.

    On tente d'abord d'utiliser le prix promotionnel (discount_price) si présent et inférieur
    au prix normal. Sinon on utilise le prix normal (price). On ajoute quelques
    fallback (sale_price, unit_price, price_ht) pour compatibilité.
    """
    promo = getattr(product, "discount_price", None)
    price = getattr(product, "price", None)
    if promo is not None:
        try:
            promo_dec = Decimal(str(promo))
            price_dec = Decimal(str(price)) if price is not None else None
            if price_dec is not None and Decimal("0") < promo_dec < price_dec:
                return promo_dec
        except Exception:
            pass
    if price is not None:
        try:
            return Decimal(str(price))
        except Exception:
            pass
    for attr in ("sale_price", "unit_price", "price_ht"):
        if hasattr(product, attr):
            val = getattr(product, attr)
            if val is not None:
                return _to_decimal(val)
    return Decimal("0.00")

@dataclass
class CartRow:
    """Représente une ligne du panier avec les informations calculées."""
    product: Any
    product_id: int
    quantity: int
    unit_price: Decimal

    @property
    def total_price(self) -> Decimal:
        return self.unit_price * self.quantity


class Cart:
    """
    Panier basé sur la session utilisateur.

    - Le panier est stocké dans request.session[CART_SESSION_ID] comme un dict
      {"<product_id>": {"qty": int, "unit_price": str}}
    - L'API est tolérante : on peut utiliser product ou product_id, qty ou quantity.
    - Lorsque la quantité passe à 0 ou moins, la ligne est supprimée.
    - Respecte un MIN_QTY global configurable et le min_order_qty/pcb_qty du produit.
    """

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if cart is None:
            cart = self.session[CART_SESSION_ID] = {}
        self._cart: Dict[str, Dict[str, Any]] = cart

    def _save(self) -> None:
        self.session[CART_SESSION_ID] = self._cart
        self.session.modified = True


    def add(
        self,
        product: Optional[Any] = None,
        product_id: Optional[int] = None,
        qty: Optional[int] = None,
        quantity: Optional[int] = None,
        override: bool = False,
    ) -> None:
        """
        Ajoute ou met à jour une ligne du panier.

        Paramètres :
          - product ou product_id (au moins un requis)
          - qty (ancien nom) ou quantity (nouvel alias) : quantité à ajouter
          - override : si True, remplace la quantité existante au lieu d’additionner
        La fonction applique ensuite les règles de quantité minimale et de multiples
        de PCB si configuré.
        """
        pid = product_id or getattr(product, "id", None)
        if pid is None:
            raise ValueError("add() requiert product ou product_id")
        pid_str = str(int(pid))
        q = qty if qty is not None else quantity
        try:
            q_int = int(q) if q is not None else 1
        except Exception:
            q_int = 1
        current = int(self._cart.get(pid_str, {}).get("qty", 0))
        product_obj = product or Product.objects.get(pk=int(pid))

        min_qty = MIN_QTY
        prod_min = getattr(product_obj, "min_order_qty", None)
        if isinstance(prod_min, int) and prod_min > 0:
            min_qty = max(min_qty, prod_min)

        pcb = None
        order_in_packs = getattr(product_obj, "order_in_packs", False)
        if order_in_packs:
            try:
                pcb_val = int(getattr(product_obj, "pcb_qty", 1))
                if pcb_val > 1:
                    pcb = pcb_val
            except Exception:
                pcb = None

        new_qty = q_int if override else (current + q_int)
        if new_qty <= 0:
            if pid_str in self._cart:
                del self._cart[pid_str]
                self._save()
            return
        if new_qty < min_qty:
            new_qty = min_qty
        if pcb:
            new_qty = ((new_qty + pcb - 1) // pcb) * pcb

        self._cart[pid_str] = {
            "qty": new_qty,
            "unit_price": str(_unit_price_of(product_obj)),
        }
        self._save()

    def update(self, product_id: int, qty: int) -> None:
        """Fixe la quantité à qty (>=0)."""
        self.add(product_id=product_id, qty=qty, override=True)

    def remove(self, product_id: int) -> None:
        pid_str = str(int(product_id))
        if pid_str in self._cart:
            del self._cart[pid_str]
            self._save()

    def clear(self) -> None:
        self._cart = {}
        self._save()

    def __len__(self) -> int:
        return sum(int(v.get("qty", 0)) for v in self._cart.values())

    @cached_property
    def _products_map(self) -> Dict[int, Any]:
        ids = [int(pid) for pid in self._cart.keys()]
        qs = Product.objects.filter(id__in=ids)
        return {p.id: p for p in qs}

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """Itère sur les lignes du panier en enrichissant avec le produit et les prix."""
        for pid_str, entry in self._cart.items():
            pid = int(pid_str)
            product_obj = self._products_map.get(pid)
            if not product_obj:
                continue
            qty = int(entry.get("qty", 0))
            if qty <= 0:
                continue
            unit_price = _to_decimal(entry.get("unit_price", "0.00"))
            yield {
                "product": product_obj,
                "product_id": pid,
                "quantity": qty,
                "qty": qty,  # alias tolérant
                "unit_price": unit_price,
                "price": unit_price,  # alias tolérant
                "total_price": unit_price * qty,
                "total": unit_price * qty,  # alias tolérant
            }

    @property
    def total(self) -> Decimal:
        total = Decimal("0.00")
        for it in self:
            total += it["total_price"]
        return total

    def get_total_price(self) -> Decimal:
        """
        Méthode sans argument utilisable dans les templates :
        {{ cart.get_total_price }}
        """
        return self.total

    def items(self):
        """Alias legacy pour certains vieux codes."""
        return list(iter(self))

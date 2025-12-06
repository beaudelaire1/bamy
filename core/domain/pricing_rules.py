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
        """Applique la grille B2B sur un *objet compatible DTO*.

        ``user`` et ``product`` sont traités en mode duck-typing : le domaine
        n'a pas besoin de connaître la nature exacte de l'objet (DTO Pydantic
        ou simple objet avec les bons attributs).
        """
        if user is None:
            return None

        client_type = getattr(user, "client_type", None)
        if client_type not in {"wholesaler", "big_retail", "small_retail"}:
            # Pas de grille B2B pour ce type de client.
            return None

        if client_type == "wholesaler":
            base = getattr(product, "price_wholesaler", None) or product.price
        elif client_type == "big_retail":
            base = getattr(product, "price_big_retail", None) or product.price
        else:  # small_retail
            base = getattr(product, "price_small_retail", None) or product.price

        price = Decimal(base)

        # Surcharge compte non vérifié : +5% sur le prix B2B.
        if not getattr(user, "is_b2b_verified", False):
            price = (price * Decimal("1.05")).quantize(Decimal("0.01"))

        return price


class AdvancedPricingRules:
    """Règles avancées de tarification entreprise.

    Ces règles s'appliquent après que le prix de base (promo, grille
    B2B, discount simple) a été calculé.  Elles permettent d'offrir
    des remises supplémentaires en fonction de la quantité commandée,
    de la marque ou de la famille de produits, tout en respectant un
    prix plancher minimal.
    """

    # Tableaux simples de remise par quantité.  Dans un cas réel ces
    # valeurs seraient stockées en base ou configurables.  Ici on
    # applique 10 % de remise à partir de 50 unités et 20 % à partir
    # de 100 unités.  Les valeurs sont exprimées en pourcentage.
    QUANTITY_DISCOUNTS = {
        100: Decimal("0.20"),
        50: Decimal("0.10"),
    }
    # Remises par marque (slug ou nom) → pourcentage.
    BRAND_DISCOUNTS = {
        "acme": Decimal("0.05"),  # 5 % de remise sur la marque Acme
    }
    # Remises par famille de produits (catégorie) → pourcentage.
    FAMILY_DISCOUNTS = {
        "Electronics": Decimal("0.03"),
    }
    # Prix plancher exprimé en pourcentage du prix public.  Le prix
    # final ne descendra jamais en dessous de 70 % du prix public.
    FLOOR_PERCENT = Decimal("0.70")

    @classmethod
    def apply_quantity_discount(cls, unit_price: Decimal, quantity: int) -> Decimal:
        """Calcule un prix unitaire après remise par quantité.

        Les remises sont cumulables avec la grille B2B et les promos.
        La remise la plus élevée applicable est choisie (ex: pour
        120 unités, la remise de 20 % s'applique).
        """
        discount_rate = Decimal("0")
        for threshold, rate in sorted(cls.QUANTITY_DISCOUNTS.items(), reverse=True):
            if quantity >= threshold:
                discount_rate = rate
                break
        if discount_rate > 0:
            unit_price = (unit_price * (Decimal("1.0") - discount_rate)).quantize(
                Decimal("0.01")
            )
        return unit_price

    @classmethod
    def apply_brand_discount(
        cls,
        unit_price: Decimal,
        brand_slug: Optional[str] = None,
        brand_name: Optional[str] = None,
    ) -> Decimal:
        """Applique une remise en fonction de la marque.

        Le domaine ne dépend plus d'un objet produit concret ; seules les
        informations nécessaires (slug / nom de la marque) sont passées.
        """
        discount_rate = Decimal("0")
        if brand_slug and brand_slug.lower() in cls.BRAND_DISCOUNTS:
            discount_rate = cls.BRAND_DISCOUNTS[brand_slug.lower()]
        elif brand_name and brand_name in cls.BRAND_DISCOUNTS:
            discount_rate = cls.BRAND_DISCOUNTS[brand_name]
        if discount_rate > 0:
            unit_price = (unit_price * (Decimal("1.0") - discount_rate)).quantize(
                Decimal("0.01")
            )
        return unit_price

    @classmethod
    def apply_family_discount(
        cls,
        unit_price: Decimal,
        category_name: Optional[str] = None,
    ) -> Decimal:
        """Applique une remise basée sur la catégorie du produit.

        Si le nom de la catégorie du produit figure dans
        ``FAMILY_DISCOUNTS``, la remise correspondante est appliquée.
        """
        discount_rate = Decimal("0")
        if category_name and category_name in cls.FAMILY_DISCOUNTS:
            discount_rate = cls.FAMILY_DISCOUNTS[category_name]
        if discount_rate > 0:
            unit_price = (unit_price * (Decimal("1.0") - discount_rate)).quantize(
                Decimal("0.01")
            )
        return unit_price

    @classmethod
    def apply_floor(cls, unit_price: Decimal, public_price: Optional[Decimal]) -> Decimal:
        """Assure que le prix ne descend pas sous un prix plancher.

        Le prix plancher est défini comme un pourcentage du prix public.
        Si le prix actuel est inférieur à ce minimum, on le remonte au
        prix plancher.
        """
        if public_price is None:
            return unit_price
        floor_price = (Decimal(public_price) * cls.FLOOR_PERCENT).quantize(Decimal("0.01"))
        return unit_price if unit_price >= floor_price else floor_price

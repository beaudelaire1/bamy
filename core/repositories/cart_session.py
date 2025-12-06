from __future__ import annotations

# Importation du panier basé session.  On ignore le type car cette
# classe n'est pas définie dans le domaine et dépend de Django.
from cart.cart import Cart  # type: ignore
from core.domain.dto import CartDTO, CartItemDTO, ProductDTO
from core.interfaces import CartRepository


class SessionCartRepository(CartRepository):
    """
    Adapteur entre l'objet Cart basé session et les DTOs du domaine.
    """

    def get_for_request(self, request) -> CartDTO:
        """Construit un ``CartDTO`` à partir des données stockées en session.

        Cette implémentation ne calcule aucun prix.  Elle convertit
        uniquement les identifiants de produit et les quantités en
        ``CartItemDTO`` contenant un ``ProductDTO`` minimal.  Le calcul
        du prix est délégué au service de panier.
        """
        cart_obj = Cart(request)
        items: list[CartItemDTO] = []
        for entry in cart_obj:
            product = entry["product"]
            # Construit un ProductDTO avec les seules informations
            # nécessaires pour identifier le produit et calculer les prix
            product_dto = ProductDTO(
                id=product.id,
                sku=getattr(product, "article_code", "") or getattr(product, "sku", ""),
                price=getattr(product, "price", None),
                discount_price=getattr(product, "discount_price", None),
                price_wholesaler=getattr(product, "price_wholesaler", None),
                price_big_retail=getattr(product, "price_big_retail", None),
                price_small_retail=getattr(product, "price_small_retail", None),
                title=getattr(product, "title", None),
                is_active=getattr(product, "is_active", None),
                unit_price=None,
            )
            items.append(CartItemDTO(product=product_dto, quantity=entry["quantity"]))
        user_id = request.user.id if getattr(request.user, "is_authenticated", False) else None
        return CartDTO(user_id=user_id, items=items, total=None)

    def save_for_request(self, request, cart: CartDTO) -> CartDTO:
        """Persiste la liste des articles du panier en session.

        Seuls les identifiants de produit et les quantités sont
        stockés.  Les informations de prix et autres attributs sont
        volontairement ignorées afin de respecter la règle du single
        source of truth pour les calculs financiers.
        """
        cart_obj = Cart(request)
        cart_obj.clear()
        for item in cart.items:
            cart_obj.add(
                product_id=item.product.id,
                quantity=item.quantity,
                override=False,
            )
        # Après persistance, on ne calcule plus le total ici ; il
        # restera ``None`` jusqu'à ce que le service de panier applique
        # le moteur de pricing.
        return CartDTO(user_id=cart.user_id, items=cart.items, total=None)

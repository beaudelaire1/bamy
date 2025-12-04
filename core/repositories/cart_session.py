from __future__ import annotations

from decimal import Decimal



from core.interfaces import CartRepository, CartDTO, CartItemDTO


class SessionCartRepository(CartRepository):
    """
    Adapteur entre l'objet Cart basé session et les DTOs du domaine.
    """

    def get_for_request(self, request) -> CartDTO:
        cart_obj = Cart(request)
        items: list[CartItemDTO] = []
        for item in cart_obj:
            product = item["product"]
            items.append(
                CartItemDTO(
                    product_id=product.id,
                    sku=getattr(product, "article_code", str(product.pk)),
                    quantity=item["quantity"],
                    unit_price=item["price"],
                    total_price=item["total_price"],
                )
            )
        total = cart_obj.get_total_price() if hasattr(cart_obj, "get_total_price") else Decimal("0")
        user_id = request.user.id if request.user.is_authenticated else None
        return CartDTO(user_id=user_id, items=items, total=total)

    def save_for_request(self, request, cart: CartDTO) -> CartDTO:
        cart_obj = Cart(request)
        cart_obj.clear()
        for item in cart.items:
            cart_obj.add(
                product_id=item.product_id,
                quantity=item.quantity,
                override_quantity=False,
            )
        # Recalcule le total via l'objet Cart
        total = cart_obj.get_total_price() if hasattr(cart_obj, "get_total_price") else Decimal("0")
        return CartDTO(user_id=cart.user_id, items=cart.items, total=total)

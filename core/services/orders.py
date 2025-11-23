from __future__ import annotations

from core.interfaces import CartRepository, OrderRepository, OrderDTO


class OrderService:
    """
    Service métier pour la création et la consultation des commandes.
    """

    def __init__(self, cart_repo: CartRepository, order_repo: OrderRepository) -> None:
        self.cart_repo = cart_repo
        self.order_repo = order_repo

    def create_order_from_current_cart(self, request, user_id: int | None) -> OrderDTO:
        cart = self.cart_repo.get_for_request(request)
        if not cart.items:
            raise ValueError("Impossible de créer une commande depuis un panier vide.")
        order = self.order_repo.create_from_cart(cart, user_id=user_id)
        return order

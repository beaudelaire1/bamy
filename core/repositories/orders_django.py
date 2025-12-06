from __future__ import annotations

from decimal import Decimal
from typing import Iterable

from orders.models import Order, OrderItem
from core.interfaces import OrderRepository, OrderDTO, CartDTO


class DjangoOrderRepository(OrderRepository):
    """
    Implémentation du repository de commandes basée sur les modèles Django.
    """

    def _to_dto(self, obj: Order) -> OrderDTO:
        return OrderDTO(
            id=obj.id,
            order_number=obj.order_number or str(obj.id),
            user_id=obj.user_id,
            total=obj.get_total_amount() if hasattr(obj, "get_total_amount") else obj.total,
            status=obj.status,
        )

    def create_from_cart(self, cart: CartDTO, user_id: int | None) -> OrderDTO:
        """Crée une commande à partir d'un ``CartDTO``.

        Les identifiants de produit et les quantités sont extraits du
        ``product`` contenu dans chaque ``CartItemDTO``.  Le prix
        unitaire est lu directement depuis la ligne.  Le total de la
        commande est fourni par le cart.
        """
        order = Order.objects.create(
            user_id=user_id,
            total=cart.total or 0,
            status="pending",
        )
        for item in cart.items:
            OrderItem.objects.create(
                order=order,
                product_id=item.product.id,
                quantity=item.quantity,
                price=item.unit_price,
            )
        return self._to_dto(order)

    def list_for_user(self, user_id: int) -> Iterable[OrderDTO]:
        qs = Order.objects.filter(user_id=user_id).order_by("-created_at")
        return [self._to_dto(o) for o in qs]

    def get_for_user(self, order_id: int, user_id: int) -> OrderDTO:
        obj = Order.objects.get(id=order_id, user_id=user_id)
        return self._to_dto(obj)

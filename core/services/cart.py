from __future__ import annotations

from decimal import Decimal

from core.interfaces import (
    ProductRepository,
    CartRepository,
    PricingService,
    CartDTO,
    CartItemDTO,
)


class CartService:
    """
    Service métier pour la gestion du panier B2B.

    Cette classe encapsule toute la logique métier liée au panier
    afin de la sortir des vues Django/DRF. Elle ne dépend que des
    interfaces déclarées dans ``core.interfaces``.
    """

    def __init__(
        self,
        product_repo: ProductRepository,
        cart_repo: CartRepository,
        pricing_service: PricingService,
    ) -> None:
        self.product_repo = product_repo
        self.cart_repo = cart_repo
        self.pricing_service = pricing_service

    def get_cart(self, request, client_type: str | None = None) -> CartDTO:
        cart = self.cart_repo.get_for_request(request)
        # Éventuellement recalculer les totaux ici
        return cart

    def add_item(
        self,
        request,
        sku: str,
        quantity: int,
        client_type: str | None = None,
    ) -> CartDTO:
        if quantity <= 0:
            raise ValueError("La quantité doit être positive.")

        cart = self.cart_repo.get_for_request(request)
        product = self.product_repo.get_by_sku(sku)
        unit_price = self.pricing_service.compute_unit_price(product, client_type)

        items: list[CartItemDTO] = []
        found = False
        for item in cart.items:
            if item.product_id == product.id:
                new_qty = item.quantity + quantity
                total_price = unit_price * Decimal(new_qty)
                items.append(
                    CartItemDTO(
                        product_id=product.id,
                        sku=product.sku,
                        quantity=new_qty,
                        unit_price=unit_price,
                        total_price=total_price,
                    )
                )
                found = True
            else:
                items.append(item)

        if not found:
            total_price = unit_price * Decimal(quantity)
            items.append(
                CartItemDTO(
                    product_id=product.id,
                    sku=product.sku,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price,
                )
            )

        cart.items = items
        cart.total = sum((it.total_price for it in cart.items), Decimal("0"))
        return self.cart_repo.save_for_request(request, cart)

    def clear(self, request) -> CartDTO:
        cart = self.cart_repo.get_for_request(request)
        cart.items = []
        cart.total = Decimal("0")
        return self.cart_repo.save_for_request(request, cart)

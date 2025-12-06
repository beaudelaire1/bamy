from __future__ import annotations

from decimal import Decimal

from core.interfaces import (
    ProductRepository,
    CartRepository,
    PricingService,
    CartDTO,
    CartItemDTO,
    ProductDTO,
    UserDTO,
)
from core.utils.auth import get_current_client


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
        """Retourne le panier courant, recalculé via le service de tarification.

        La méthode récupère les lignes de panier auprès du repository puis
        délègue le calcul des prix au ``PricingService.calculate_cart``.  Le
        panier retourné contient des ``unit_price`` et ``total_price``
        cohérents et un ``total`` mis à jour.
        """
        cart = self.cart_repo.get_for_request(request)
        # Construit un UserDTO à partir de la requête.  Certaines
        # installations peuvent ne pas disposer du modèle utilisateur ou
        # des champs attendus, c'est pourquoi nous utilisons getattr avec
        # des valeurs par défaut.
        user_dto: UserDTO | None = None
        user = getattr(request, "user", None)
        if user is not None and getattr(user, "is_authenticated", False):
            # Utilise le helper pour récupérer le contexte client
            client_ctx = get_current_client(user)
            user_dto = UserDTO(
                id=user.id,
                email=getattr(user, "email", ""),
                client_type=client_ctx.client_type,
                customer_number=getattr(user, "customer_number", None),
                is_b2b_verified=getattr(user, "is_b2b_verified", False),
                pricing_mode=client_ctx.pricing_mode,
            )
        # Délègue le calcul des prix au service de tarification
        pricing_result = self.pricing_service.calculate_cart(cart.items, user_dto)
        return CartDTO(user_id=cart.user_id, items=pricing_result.items, total=pricing_result.total)

    def add_item(
        self,
        request,
        sku: str,
        quantity: int,
        client_type: str | None = None,
    ) -> CartDTO:
        if quantity <= 0:
            raise ValueError("La quantité doit être positive.")

        # Récupère l'état courant du panier (ids et quantités)
        cart = self.cart_repo.get_for_request(request)
        # Récupère le produit via le repository ; le repository fournit un
        # ``ProductDTO`` avec un ``unit_price`` initial (qui sera
        # recalculé plus tard)
        product: ProductDTO = self.product_repo.get_by_sku(sku)
        # Met à jour la liste des items en modifiant uniquement la quantité
        items: list[CartItemDTO] = []
        found = False
        for item in cart.items:
            if item.product.id == product.id:
                new_qty = item.quantity + quantity
                items.append(CartItemDTO(product=item.product, quantity=new_qty))
                found = True
            else:
                items.append(item)
        if not found:
            items.append(CartItemDTO(product=product, quantity=quantity))
        # Met à jour le panier stocké dans la session (sans prix)
        cart.items = items
        cart.total = None
        persisted = self.cart_repo.save_for_request(request, cart)
        # Reconstruit le UserDTO pour le recalcul des prix
        user_dto: UserDTO | None = None
        user = getattr(request, "user", None)
        if user is not None and getattr(user, "is_authenticated", False):
            client_ctx = get_current_client(user)
            user_dto = UserDTO(
                id=user.id,
                email=getattr(user, "email", ""),
                client_type=client_ctx.client_type,
                customer_number=getattr(user, "customer_number", None),
                is_b2b_verified=getattr(user, "is_b2b_verified", False),
                pricing_mode=client_ctx.pricing_mode,
            )
        # Calcule les prix sur les lignes mises à jour
        pricing_result = self.pricing_service.calculate_cart(persisted.items, user_dto)
        return CartDTO(user_id=persisted.user_id, items=pricing_result.items, total=pricing_result.total)

    def clear(self, request) -> CartDTO:
        """Vide complètement le panier et retourne un DTO vide.

        Le repository est responsable de réinitialiser la session.  Les
        valeurs de prix sont remises à zéro pour garantir qu'aucun
        calcul n'est réalisé côté panier.
        """
        cart = self.cart_repo.get_for_request(request)
        cart.items = []
        cart.total = None
        persisted = self.cart_repo.save_for_request(request, cart)
        return CartDTO(user_id=persisted.user_id, items=[], total=Decimal("0"))

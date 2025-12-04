from typing import Optional

from django.utils import timezone

from catalog.models import PromoCatalog, PromoItem
from core.domain.dto import PromoItemDTO, ProductDTO, UserDTO


class DjangoPromoCatalogAdapter:
    """Adapter ORM pour les catalogues de promotion.

    Cette implémentation applique les règles suivantes :

    - Seuls les catalogues actifs et dans la fenêtre de dates
      (start_date <= maintenant <= end_date) sont pris en compte.
    - Une promo n'est applicable que si le produit est présent dans
      le catalogue ET si le numéro client de l'utilisateur figure
      dans ``allowed_customer_numbers`` de l'item.
    """

    def get_applicable_promo(
        self,
        product_dto: ProductDTO,
        user_dto: Optional[UserDTO] = None,
    ) -> Optional[PromoItemDTO]:
        if user_dto is None or not user_dto.customer_number:
            return None

        now = timezone.now()

        catalogs_qs = PromoCatalog.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now,
        )

        item = (
            PromoItem.objects.filter(
                product_id=product_dto.id,
                catalog__in=catalogs_qs,
                allowed_customer_numbers__contains=[user_dto.customer_number],
            )
            .order_by("id")
            .first()
        )

        if not item:
            return None

        return PromoItemDTO(promo_price=item.promo_price)


from catalog.models import PromoCatalog, PromoItem
from django.db import models
from django.utils import timezone
from core.domain.dto import PromoItemDTO

class DjangoPromoCatalogAdapter:
    def get_applicable_promo(self, product_dto, user_dto):
        now = timezone.now()
        qs = PromoCatalog.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).filter(
            models.Q(target_users__id=user_dto.id) |
            models.Q(target_client_type=user_dto.client_type)
        )
        item = PromoItem.objects.filter(
            product_id=product_dto.id,
            catalog__in=qs
        ).first()
        if not item:
            return None
        return PromoItemDTO(promo_price=item.promo_price)

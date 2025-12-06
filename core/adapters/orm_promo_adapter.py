from typing import Optional

from django.utils import timezone

from catalog.models import PromoCatalog, PromoItem
from decimal import Decimal
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
        """Retourne la promotion applicable à ``product_dto`` pour ``user_dto``.

        Cette implémentation respecte l'ordre et les conditions suivantes :

        * Seuls les catalogues actifs et dans la fenêtre de dates
          (``start_date <= now <= end_date``) sont considérés.
        * Le ciblage peut être défini à deux niveaux :
            - au niveau du catalogue via ``target_client_type`` ou ``target_users`` ;
            - au niveau de l'item via ``allowed_customer_numbers`` (liste de numéros clients).
        * Un item est applicable si :
            - le produit est dans l'item ;
            - ``allowed_customer_numbers`` contient ``user_dto.customer_number`` ou est vide ;
            - ET le catalogue est soit non ciblé (``target_client_type`` et ``target_users`` vides),
              soit il cible explicitement ``user_dto.client_type`` via ``target_client_type``,
              soit ``user_dto.id`` est dans ``target_users``.
        * En cas de chevauchement de plusieurs promos applicables, on choisit celle
          offrant le prix le plus bas (``promo_price``) afin d'éviter des
          incohérences. Si les prix sont identiques, on prend l'item le plus récent.

        Si aucun ``user_dto`` n'est fourni ou si l'utilisateur ne possède pas
        de numéro client, aucune promo catalogue ne s'applique et ``None`` est retourné.
        """

        # Sans utilisateur ou sans numéro client, pas de promo catalogue ciblée.
        if user_dto is None or not user_dto.customer_number:
            return None

        now = timezone.now()
        # Récupère les catalogues actifs et dans la fenêtre de validité
        catalogs_qs = PromoCatalog.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now,
        )

        # Récupère tous les items du produit dans ces catalogues actifs
        items_qs = PromoItem.objects.filter(
            product_id=product_dto.id,
            catalog__in=catalogs_qs,
        )

        # Applique un filtrage de base sur les numéros clients : un item est
        # candidat s'il ne restreint pas ``allowed_customer_numbers`` ou
        # si le numéro client de l'utilisateur est présent dans la liste.
        from django.db.models import Q
        items_qs = items_qs.filter(
            Q(allowed_customer_numbers__isnull=True) |
            Q(allowed_customer_numbers__exact=[]) |
            Q(allowed_customer_numbers__contains=[user_dto.customer_number])
        )

        candidates: list[tuple[int, Decimal, int, PromoItem]] = []
        for item in items_qs.select_related("catalog"):
            # Vérifie à nouveau les numéros clients pour déterminer la priorité
            allowed = item.allowed_customer_numbers or []
            priority = 4
            if allowed and user_dto.customer_number in allowed:
                priority = 1
            else:
                catalog = item.catalog
                # Ciblage explicite par utilisateurs
                try:
                    # ManyToManyField ``target_users`` peut être vide ou None
                    if catalog.target_users and catalog.target_users.filter(id=user_dto.id).exists():
                        priority = 2
                    elif catalog.target_client_type:
                        if catalog.target_client_type == user_dto.client_type:
                            priority = 3
                        else:
                            priority = 4
                    else:
                        priority = 4
                except Exception:
                    # Si la relation n'est pas chargée ou absente, on considère qu'il n'y a pas de ciblage
                    if getattr(catalog, "target_client_type", None) == user_dto.client_type:
                        priority = 3
                    else:
                        priority = 4
            # Utilise l'identifiant négatif pour favoriser les items récents
            candidates.append((priority, item.promo_price, -item.id, item))

        if not candidates:
            return None
        # Trie par priorité croissante, puis par prix croissant, puis par id décroissant
        candidates.sort()
        selected_item = candidates[0][3]
        return PromoItemDTO(promo_price=selected_item.promo_price)

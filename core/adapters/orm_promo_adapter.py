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

        # Filtre les catalogues selon le ciblage client_type ou utilisateur.
        # Un catalogue est considéré applicable si :
        # - target_client_type est vide ou égal au client_type de l'utilisateur ;
        # - ET target_users est vide ou contient l'utilisateur.
        from django.db.models import Q
        catalogs_qs = catalogs_qs.filter(
            # Un catalogue sans ciblage client_type ou dont le client_type correspond à celui de l'utilisateur
            Q(target_client_type__isnull=True) | Q(target_client_type__exact="") | Q(target_client_type=user_dto.client_type),
            # Un catalogue sans ciblage explicite d'utilisateurs ou contenant cet utilisateur
            Q(target_users__isnull=True) | Q(target_users=user_dto.id),
        ).distinct()

        # Recherche les items correspondant au produit et au ciblage.
        # On sélectionne à la fois les items dont allowed_customer_numbers contient
        # explicitement le numéro client, et ceux dont la liste est vide (promo
        # ouverte à tous les clients du catalogue).
        items_qs = PromoItem.objects.filter(
            product_id=product_dto.id,
            catalog__in=catalogs_qs,
        ).filter(
            Q(allowed_customer_numbers__contains=[user_dto.customer_number]) |
            Q(allowed_customer_numbers__exact=[]) |
            Q(allowed_customer_numbers__isnull=True)
        )

        # Ordre de tri : d'abord par prix croissant, puis par identifiant décroissant (promo la plus récente).
        item = items_qs.order_by('promo_price', '-id').first()

        if not item:
            return None

        return PromoItemDTO(promo_price=item.promo_price)

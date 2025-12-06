"""Filtres personnalisés pour l'application catalog.

Ce module définit des filtres utiles dans les templates, notamment
pour calculer et afficher le prix d'un produit en fonction d'un
utilisateur donné.  Les filtres sont enregistrés via l'instance
``Library`` de Django.
"""

from django import template

# Le filtre price_for_user sert à calculer le tarif d'un produit en fonction
# d'un utilisateur en s'appuyant sur le service de pricing centralisé.
# Il délègue entièrement le calcul à PromoAwareB2BPricingService via
# core.factory.get_pricing_service() et ne dépend plus de méthodes sur le
# modèle Product (qui ne doit pas contenir de logique métier).


register = template.Library()


@register.filter
def price_for_user(product, user):
    """Retourne le prix d'un ``product`` ajusté selon les règles de pricing pour ``user``.

    Ce filtre est destiné à être utilisé dans les gabarits :
    ``{{ product|price_for_user:request.user }}``.

    Il s'appuie sur le moteur central de pricing pour appliquer, dans l'ordre :
    1. les promotions catalogue ciblées (par numéro client ou type de client),
    2. la grille tarifaire B2B (wholesaler/big_retail/small_retail) avec surcharge pour compte non vérifié,
    3. la promotion simple ``discount_price``,
    4. le prix public ``price`` en dernier recours.

    Parameters
    ----------
    product : catalog.models.Product
        L'instance du produit à tarifer.
    user : django.contrib.auth.models.User
        L'utilisateur pour lequel on souhaite calculer le prix. Peut être ``None``.

    Returns
    -------
    decimal.Decimal or None
        Le prix ajusté si possible, sinon ``None`` (par exemple pour un visiteur non authentifié).
    """
    if not product:
        return None
    try:
        pricing_service = get_pricing_service()
        # Le service renvoie toujours un Decimal. Pour un visiteur non connecté,
        # on retourne None afin de permettre aux templates d'afficher un message
        # invitant à se connecter pour voir les prix.
        result = pricing_service.get_unit_price(product, user)
        return result
    except Exception:
        # En cas d'erreur inattendue (par exemple mauvaise configuration), ne
        # renvoie pas d'exception dans les templates mais retourne ``None``.
        return None
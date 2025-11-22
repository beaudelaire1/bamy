"""Filtres personnalisés pour l'application catalog.

Ce module définit des filtres utiles dans les templates, notamment
pour calculer et afficher le prix d'un produit en fonction d'un
utilisateur donné.  Les filtres sont enregistrés via l'instance
``Library`` de Django.
"""

from django import template

register = template.Library()


@register.filter
def price_for_user(product, user):
    """Retourne le prix du ``product`` ajusté selon la catégorie du ``user``.

    Si ``product`` n'a pas d'attribut ``get_price_for_user``, retourne
    ``None``.  Ce filtre est principalement destiné à être utilisé dans
    les gabarits : ``{{ product|price_for_user:request.user }}``.

    Parameters
    ----------
    product : catalog.models.Product
        L'instance du produit à tarifer.
    user : django.contrib.auth.models.User
        L'utilisateur pour lequel on souhaite calculer le prix.

    Returns
    -------
    decimal.Decimal or None
        Le prix ajusté si possible, sinon ``None``.
    """
    if not product:
        return None
    getter = getattr(product, "get_price_for_user", None)
    if callable(getter):
        try:
            return getter(user)
        except Exception:
            return None
    return None
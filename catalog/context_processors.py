"""
Context processors for the catalog app.

These helpers expose common catalog data to all templates. In particular,
`nav_categories` provides a list of active top‑level categories for the
navigation bar so visitors can quickly access product categories from
any page. Displaying categories in the header is considered a best
practice for e‑commerce sites to improve browsing and discovery【57097290496292†L176-L182】.
"""

from .models import Category


def categories(request):
    """Expose active root categories for use in the global navigation bar.

    Returns a dictionary with a single key, ``nav_categories``, which
    contains a queryset of categories that have no parent and are marked
    as active. These categories can be iterated in templates to build
    a dropdown or mega menu.
    """
    try:
        cats = Category.objects.filter(parent__isnull=True, is_active=True)
    except Exception:
        # In case of migration or database issues, return an empty queryset
        cats = Category.objects.none()
    return {
        "nav_categories": cats,
    }
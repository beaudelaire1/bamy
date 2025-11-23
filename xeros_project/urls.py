from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from catalog.sitemaps import CategorySitemap, ProductSitemap, BrandSitemap
from core.sitemaps import StaticViewSitemap

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls", namespace="core")),
    path("accounts/", include("userauths.urls", namespace="userauths")),
    path("cart/", include("cart.urls", namespace="cart")),
    path("catalog/", include("catalog.urls", namespace="catalog")),
    path("orders/", include("orders.urls", namespace="orders")),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("payments/", include("payments.urls", namespace="payments")),
    # Avis produits et API REST
    path("reviews/", include("reviews.urls", namespace="reviews")),
    # L'API REST n'est disponible que si le module api est présent.
    # On encapsule l'import dans un bloc try pour éviter une erreur
    # ``ModuleNotFoundError`` lorsque ``rest_framework`` ou l'app ``api``
    # n'est pas installé.
]

# Intégration conditionnelle de l'API.  Si l'app ``api.urls`` est
# disponible, on l'inclut dans les URL patterns.  Sinon, on ignore
try:
    import api.urls  # type: ignore
    urlpatterns.append(path("api/", include("api.urls")))
except Exception:
    # L'API n'est pas installée : pas d'URL /api/
    pass

urlpatterns += [
    # CRM, notifications et intégrations
    path("crm/", include("crm.urls", namespace="crm")),
    path("notifications/", include("notifications.urls", namespace="notifications")),
    path("integrations/", include("integrations.urls", namespace="integrations")),

    # Gestion des retours
    path("returns/", include("returns.urls", namespace="returns")),

    # Marketing (newsletter, campagnes)
    path("marketing/", include("marketing.urls", namespace="marketing")),

    # Recrutement : offres et candidatures
    path("recruitment/", include("recruitment.urls", namespace="recruitment")),

    # Programme de fidélité
    path("loyalty/", include("loyalty.urls", namespace="loyalty")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# -------------------------------------------------------------------
# SEO : sitemap et robots.txt
#
# Le sitemap combine plusieurs sections : catégories, produits, marques et pages
# statiques. Le fichier robots.txt est servi via TemplateView.
sitemaps = {
    "categories": CategorySitemap,
    "products": ProductSitemap,
    "brands": BrandSitemap,
    "static": StaticViewSitemap,
}

urlpatterns += [
    path("api/",
         include("api.urls")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="robots.txt", content_type="text/plain"
        ),
        name="robots",
    ),
]



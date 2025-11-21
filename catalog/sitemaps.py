from django.contrib.sitemaps import Sitemap
from .models import Category, Product, Brand


class CategorySitemap(Sitemap):
    """
    Sitemap pour les catégories.
    Liste uniquement les catégories actives et génère l'URL via get_absolute_url.
    """

    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Category.objects.filter(is_active=True)

    def location(self, obj):
        return obj.get_absolute_url()


class ProductSitemap(Sitemap):
    """
    Sitemap pour les produits.
    Liste uniquement les produits actifs et génère l'URL via get_absolute_url.
    """

    changefreq = "daily"
    priority = 0.6

    def items(self):
        return Product.objects.filter(is_active=True)

    def location(self, obj):
        return obj.get_absolute_url()


class BrandSitemap(Sitemap):
    """
    Sitemap pour les marques.
    Liste uniquement les marques actives et génère l'URL via get_absolute_url.
    """

    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Brand.objects.filter(is_active=True)

    def location(self, obj):
        return obj.get_absolute_url()
from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """
    Sitemap pour les pages statiques de l'application.

    On liste ici les noms d'URL des vues qui ne dépendent pas de contenu
    dynamique (par exemple la page d'accueil). D'autres URL peuvent être
    ajoutées à mesure que l'application s'enrichit.
    """

    priority = 1.0
    changefreq = "weekly"

    def items(self):
        # Ajouter d'autres noms d'URL statiques ici si nécessaire.
        return ["core:home"]

    def location(self, item):
        return reverse(item)
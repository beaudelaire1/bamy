from django.conf import settings
from catalog.models import Category
from .models import SiteSettings

def brand(request):
    """
    Context processeur ajoutant des informations de marque et de navigation.

    Cette fonction tente d'abord de charger la configuration du site à
    partir du modèle ``SiteSettings``.  Si une instance est présente
    en base, ses champs (nom, slogan, couleurs) sont utilisés pour
    alimenter les variables de template.  À défaut, les valeurs
    définies dans ``settings.py`` sont utilisées comme fallback.

    En plus du branding, la fonction récupère également les
    catégories racines actives (les 10 premières par ordre
    alphabétique) afin de les afficher dans la barre de navigation
    principale.
    """
    # Récupération des catégories racines actives
    nav_cats = (
        Category.objects.filter(parent__isnull=True, is_active=True)
        .order_by("name")[:10]
    )

    # Tentative de lecture du branding depuis la base de données
    site_config = None
    try:
        site_config = SiteSettings.objects.first()
    except Exception:
        # La table peut ne pas exister si les migrations ne sont pas appliquées
        site_config = None

    if site_config:
        company_name = site_config.name
        company_tagline = site_config.tagline or ""
        brand_colors = {
            "PRIMARY": site_config.primary_color,
            "ACCENT": site_config.accent_color,
            "DARK": site_config.dark_color,
            "LIGHT": site_config.light_color,
        }
    else:
        # Fallback vers les paramètres settings
        company_name = getattr(settings, "COMPANY_NAME", "YourBrand")
        company_tagline = getattr(settings, "COMPANY_TAGLINE", "")
        brand_colors = getattr(settings, "BRAND", {})

    return {
        "COMPANY_NAME": company_name,
        "COMPANY_TAGLINE": company_tagline,
        "BRAND": brand_colors,
        "nav_categories": nav_cats,
    }

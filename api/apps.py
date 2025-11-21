from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Configuration de l'application API.

    Cette application expose des points d'accès REST pour nos modèles
    internes (commandes, factures, etc.) à destination de systèmes
    externes comme SAGE X3 et Biziipad. Elle se base sur
    Django REST Framework pour serialiser les données.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "api"
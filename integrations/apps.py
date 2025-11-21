from django.apps import AppConfig


class IntegrationsConfig(AppConfig):
    """
    Configuration de l'application d'intégrations tierces.
    Permet de centraliser la logique de synchronisation avec des services
    externes (catalogue, ERP, paiement, etc.).
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "integrations"
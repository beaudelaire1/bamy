from django.apps import AppConfig


class CrmConfig(AppConfig):
    """
    Configuration de l'application CRM.

    Cette app gère la base de clients B2B/B2C et permet de
    regrouper les informations de contact en un seul endroit.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "crm"
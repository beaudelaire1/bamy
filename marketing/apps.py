from django.apps import AppConfig


class MarketingConfig(AppConfig):
    """Configuration de l'application marketing.

    Cette application gère les campagnes e‑mails (newsletter,
    paniers abandonnés) et les intégrations marketing. Les tâches
    planifiées sont définies dans le fichier tasks.py.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "marketing"
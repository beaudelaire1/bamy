from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    """
    Configuration de l'application de notifications.
    Cette app gère l'envoi et la consultation de notifications internes.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "notifications"
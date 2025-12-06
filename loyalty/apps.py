from django.apps import AppConfig


class LoyaltyConfig(AppConfig):
    """Configuration de l'application de fidélité."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "loyalty"

    def ready(self) -> None:  # type: ignore[override]
        """Connect signal receivers when the app is ready.

        The loyalty app listens for the ``order_validated`` signal to
        award loyalty points after an order has been successfully
        created.  Using signals decouples the loyalty logic from the
        orders app and avoids direct imports between them.
        """
        super().ready()
        try:
            from django.dispatch import receiver  # type: ignore
            from core.signals import order_validated  # type: ignore
            from .models import LoyaltyAccount  # type: ignore

            @receiver(order_validated)
            def _award_loyalty_points(sender, order, user, **kwargs):  # type: ignore
                # Attribue des points de fidélité à l'utilisateur connecté.
                # 1 point par euro dépensé (hors centimes)
                if user is None:
                    return
                try:
                    account, _ = LoyaltyAccount.objects.get_or_create(user=user)
                    account.points = account.points + int(order.total)
                    account.save(update_fields=["points"])
                except Exception:
                    # En cas d'erreur (par exemple si l'app n'est pas migrée), on ignore
                    pass
        except Exception:
            # Les dépendances peuvent ne pas être disponibles lors de la collecte statique.
            pass
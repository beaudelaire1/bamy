"""Utilitaires d'envoi d'emails asynchrones.

Ce module fournit une fine surcouche autour de ``django.core.mail.send_mail``
qui délègue l'envoi réel à un ``ThreadPoolExecutor``. L'objectif n'est pas de
remplacer une vraie file de tâches (Celery, RQ, etc.), mais d'éviter que les
vues HTTP de checkout soient bloquées par un serveur SMTP lent.

Ce mécanisme est volontairement simple et sans dépendance externe afin de
rester utilisable dans tous les environnements (dev, préprod, petite prod).
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Any, Iterable

try:  # pragma: no cover - import seulement en contexte Django
    from django.core.mail import send_mail
except Exception:  # pragma: no cover
    def send_mail(*args: Any, **kwargs: Any) -> int:  # type: ignore[override]
        """Fallback no-op si Django n'est pas disponible.

        Permet d'importer le module dans des contextes hors Django
        (tests unitaires de domaine, scripts, etc.) sans lever
        d'ImportError.
        """

        return 0


_executor = ThreadPoolExecutor(max_workers=2)


def async_send_mail(
    subject: str,
    message: str,
    from_email: str | None,
    recipient_list: Iterable[str],
    *args: Any,
    **kwargs: Any,
) -> None:
    """Planifie l'envoi d'un email dans un thread en arrière-plan.

    L'appelant ne bloque pas sur l'envoi : il obtient immédiatement la
    main et peut continuer à rendre la réponse HTTP. Les erreurs
    d'envoi sont loguées mais ne sont pas propagées à la vue.
    """

    def _task() -> None:
        try:
            send_mail(subject, message, from_email, list(recipient_list), *args, **kwargs)
        except Exception:
            # Dans un contexte réel on brancherait ici un logger.
            pass

    _executor.submit(_task)

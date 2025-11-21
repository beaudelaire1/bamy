"""
Initialisation du paquet ``xeros_project``.

Ce module expose l'instance Celery du projet sous le nom
``celery_app``.  L'importation de ``celery_app`` garantit que la
configuration de Celery est correctement chargée et que les tasks
asynchrones peuvent être exécutées via la commande :

    celery -A xeros_project worker -l info

Le décorateur ``@shared_task`` peut être utilisé dans les autres
applications sans nécessiter de référence explicite à l'application
Celery.
"""

# Importer l'application Celery définie dans ``celery.py`` et l'exposer
# via ``celery_app``.  L'importation seule suffit à déclencher
# l'enregistrement des tasks et la configuration de Celery.
from .celery import app as celery_app  # noqa: F401

__all__ = ("celery_app",)

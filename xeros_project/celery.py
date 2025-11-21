"""
Configuration du service Celery pour le projet Xeros.

Ce module définit et configure l'application Celery utilisée pour
exécuter des tâches asynchrones au sein de l'application Django.  Il
se base sur les paramètres définis dans ``settings.py`` via le
namespace ``CELERY_*`` et cherche automatiquement les modules
``tasks.py`` dans toutes les applications installées.

Exemple d'utilisation :

    celery -A xeros_project worker -l info

Cela démarre un worker Celery qui consommera les tâches enregistrées.
Assurez-vous d'avoir configuré correctement ``CELERY_BROKER_URL`` et
``CELERY_RESULT_BACKEND`` (par exemple en pointant sur un service Redis
ou RabbitMQ) dans votre fichier ``.env`` ou dans ``settings.py``.
"""

import os

from celery import Celery

# Définit le module de configuration Django par défaut pour les tasks
# Celery.  Utilise la variable d'environnement DJANGO_SETTINGS_MODULE
# si présente, sinon se replie sur ``xeros_project.settings``.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xeros_project.settings")

# Crée l'instance d'application Celery.  Le nom de l'application
# correspond au paquet Django contenant ce fichier.
app = Celery("xeros_project")

# Lit la configuration depuis les paramètres Django.  Tous les
# paramètres commençant par ``CELERY_`` seront chargés et appliqués au
# worker Celery.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Découvre automatiquement les tasks définies dans les applications
# installées.  Celery recherchera des modules nommés ``tasks.py`` dans
# chacun des packages listés dans ``INSTALLED_APPS``.
app.autodiscover_tasks()

# Optionnel : définit un nom lisible pour les tâches lorsqu'elles
# s'exécutent.  Cela peut être utile pour le monitoring et le debug.
@app.task(bind=True)
def debug_task(self, *args, **kwargs):  # pragma: no cover - utilisation facultative
    """Une tâche de debug qui imprime son propre nom et les arguments."""
    print(f"Task {self.name!r} called with args={args} kwargs={kwargs}")

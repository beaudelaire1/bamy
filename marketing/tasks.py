"""Tâches Celery pour le marketing.

Ce module contient des tâches asynchrones et planifiées. Les tâches
sont pour l'instant des squelettes et doivent être enrichies avec la
logique d'envoi de courriels via un service (Mailchimp, Klaviyo)
et la récupération des paniers abandonnés.
"""

import datetime
from celery import shared_task


@shared_task
def send_abandoned_cart_emails():
    """Relance les paniers abandonnés.

    Cette tâche parcourra les paniers enregistrés et enverra un
    e‑mail de rappel. Dans cette version, elle se contente de
    consigner l'appel pour illustration.
    """
    # TODO: implémenter la logique de relance des paniers abandonnés.
    print(f"[Marketing] Tâche de relance des paniers abandonnés lancée à {datetime.datetime.utcnow()}")


@shared_task
def send_newsletter_campaign(newsletter_id):
    """Envoie une campagne de newsletter (squelette).

    :param newsletter_id: identifiant d'une campagne à envoyer.
    """
    # TODO: appeler l'API Mailchimp/Klaviyo pour envoyer la campagne.
    print(f"[Marketing] Envoi de la campagne {newsletter_id}")
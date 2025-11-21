"""Vues pour l'application marketing.

Cette application gère les inscriptions à la newsletter et d'autres
actions marketing (paniers abandonnés, campagnes, etc.).
"""

from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

from .models import NewsletterSubscription


def subscribe(request):
    """Inscrit un utilisateur à la newsletter.

    Accepte uniquement la méthode POST. Si une adresse email est fournie,
    crée un enregistrement de souscription ou informe l'utilisateur qu'il est
    déjà inscrit. Redirige vers la page précédente ou vers l'accueil.
    """
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        if not email:
            messages.error(request, "Merci de saisir une adresse e-mail valide.")
            return redirect(request.META.get("HTTP_REFERER", reverse("core:home")))
        obj, created = NewsletterSubscription.objects.get_or_create(email=email)
        if created:
            messages.success(request, "Votre inscription à la newsletter a été enregistrée.")
        else:
            messages.info(request, "Vous êtes déjà inscrit à la newsletter.")
        return redirect(request.META.get("HTTP_REFERER", reverse("core:home")))
    # Méthodes non autorisées : redirige simplement
    return redirect(request.META.get("HTTP_REFERER", reverse("core:home")))
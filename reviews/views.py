"""Vues pour la gestion des avis produits."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from .forms import ReviewForm
from catalog.models import Product


@login_required
def submit_review(request, product_slug: str):
    """Soumet un avis pour un produit.

    Cette vue nécessite que l'utilisateur soit connecté. Elle récupère
    le produit via son slug, instancie le formulaire et, si le POST
    est valide, enregistre l'avis et redirige vers la fiche produit
    avec un message de succès.
    """

    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    form = ReviewForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.save()
        messages.success(request, "Votre avis a été enregistré.")
        return redirect(product.get_absolute_url())
    # En cas d'échec, rediriger vers la fiche produit sans créer d'avis
    messages.error(request, "Impossible d'enregistrer votre avis.")
    return redirect(product.get_absolute_url())
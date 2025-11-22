"""Vues pour l'application de recrutement.

Cette collection de vues fournit une liste des offres d'emploi, la
consultation d'une offre individuelle et la possibilité de postuler.
Les candidatures sont enregistrées en base. Après soumission, un
message de succès est affiché et l'utilisateur est redirigé vers une
page de confirmation.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import JobPosting
from .forms import JobApplicationForm


def job_list(request):
    """Affiche la liste des offres d'emploi actives."""
    jobs = JobPosting.objects.filter(is_active=True).order_by("-published_at")
    return render(request, "recruitment/job_list.html", {"jobs": jobs})


def job_detail(request, slug):
    """Affiche le détail d'une offre d'emploi ainsi qu'un formulaire de
    candidature prêt à être rempli.

    Le formulaire est affiché mais la soumission est gérée par la vue
    :func:`job_apply` pour séparer les comportements GET et POST.
    """
    job = get_object_or_404(JobPosting, slug=slug, is_active=True)
    form = JobApplicationForm()
    return render(
        request,
        "recruitment/job_detail.html",
        {"job": job, "form": form},
    )


def job_apply(request, slug):
    """Traite l'envoi d'une candidature pour une offre donnée.

    Si la requête est POST et que le formulaire est valide, la
    candidature est enregistrée en base et l'utilisateur est
    redirigé vers une page de confirmation. Sinon, la page de
    détails de l'offre est réaffichée avec les erreurs.
    """
    job = get_object_or_404(JobPosting, slug=slug, is_active=True)
    if request.method == "POST":
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.save()
            messages.success(
                request,
                "Votre candidature a été soumise avec succès. Nous vous contacterons si votre profil correspond à nos besoins.",
            )
            return redirect("recruitment:application_success")
    else:
        form = JobApplicationForm()
    return render(
        request,
        "recruitment/job_detail.html",
        {"job": job, "form": form},
    )


def application_success(request):
    """Affiche une page de confirmation après soumission d'une candidature."""
    return render(request, "recruitment/application_success.html")
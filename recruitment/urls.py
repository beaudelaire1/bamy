"""Déclaration des routes pour l'application de recrutement."""

from django.urls import path
from . import views


app_name = "recruitment"

# L'ordre des routes est important : l'URL pour postuler doit apparaître
# avant l'URL générique du détail afin de ne pas capter « apply » comme un slug.
urlpatterns = [
    path("", views.job_list, name="job_list"),
    path("success/", views.application_success, name="application_success"),
    # La route de candidature doit précéder la route de détail
    path("<slug:slug>/apply/", views.job_apply, name="job_apply"),
    path("<slug:slug>/", views.job_detail, name="job_detail"),
]
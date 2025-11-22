"""Déclaration des routes pour l'application de recrutement."""

from django.urls import path
from . import views


app_name = "recruitment"

urlpatterns = [
    path("", views.job_list, name="job_list"),
    path("success/", views.application_success, name="application_success"),
    path("<slug:slug>/", views.job_detail, name="job_detail"),
    path("<slug:slug>/apply/", views.job_apply, name="job_apply"),
]
"""Routes pour les demandes de retour et remboursement."""

from django.urls import path
from . import views

app_name = "returns"

urlpatterns = [
    # Page de demande de retour pour un article spécifique
    path("request/<int:item_id>/", views.request_return, name="request"),

    # Page de politique de retour générale
    # Permet d'afficher les conditions et procédures de retour. Utilisée dans la navigation.
    path("", views.return_policy, name="policy"),
]
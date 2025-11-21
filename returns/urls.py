"""Routes pour les demandes de retour et remboursement."""

from django.urls import path
from . import views

app_name = "returns"

urlpatterns = [
    path("request/<int:item_id>/", views.request_return, name="request"),
]
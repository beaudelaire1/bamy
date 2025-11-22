"""Routes pour l'application de fidélité.

Cette configuration expose une seule URL pour afficher le programme de
fidélité. D'autres fonctionnalités (système de points, tableau de
bord, etc.) pourront être ajoutées ultérieurement.
"""

from django.urls import path
from . import views

app_name = "loyalty"

urlpatterns = [
    path("", views.program, name="program"),
]
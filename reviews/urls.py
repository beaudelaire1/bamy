"""Routes pour les avis produits."""

from django.urls import path
from . import views


app_name = "reviews"

urlpatterns = [
    path("<slug:product_slug>/submit/", views.submit_review, name="submit"),
]
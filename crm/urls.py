from django.urls import path
from . import views


app_name = "crm"

urlpatterns = [
    path("", views.customer_list, name="customer_list"),
    # Formulaire de contact pro
    path("contact/", views.contact_view, name="contact"),
    # Demandes de devis
    path("quote-request/", views.quote_request_view, name="quote_request"),
]
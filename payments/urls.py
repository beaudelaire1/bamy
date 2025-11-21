from django.urls import path
from . import views

app_name = "payments"
urlpatterns = [
    path("paypal/create/", views.paypal_create, name="paypal_create"),
    path("paypal/capture/", views.paypal_capture, name="paypal_capture"),
    path("stripe/checkout/", views.stripe_checkout, name="stripe_checkout"),
]
#    path("stripe/webhook/", views.stripe_webhook, name="stripe_webhook"),  # optionnel
from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("privacy/", views.privacy_policy, name="privacy"),
    path("cookies/", views.cookies_policy, name="cookies"),
    path("contact/", views.contact, name="contact"),
]

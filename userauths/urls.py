# userauths/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import RememberLoginView, logout_post, RegisterView
from .views import AccountView
from .views import (
    AddressListView,
    AddressCreateView,
    AddressUpdateView,
    AddressDeleteView,
    EmailChangeRequestView,
    EmailChangeConfirmView,
)

app_name = "userauths"  # important pour {% url 'userauths:...' %}

urlpatterns = [
    path("login/", RememberLoginView.as_view(), name="login"),
    path("logout/", logout_post, name="logout"),           # POST only
    path("register/", RegisterView.as_view(), name="register"),

    # Tableau de bord / mon compte
    path("account/", AccountView.as_view(), name="account"),

    # Tableau de bord utilisateur
    path("dashboard/", views.dashboard, name="dashboard"),

    # Vues Django auth utiles (optionnel)
    path("password_change/", auth_views.PasswordChangeView.as_view(), name="password_change"),
    path("password_change/done/", auth_views.PasswordChangeDoneView.as_view(), name="password_change_done"),
    path("password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),

    # Carnet d'adresses
    path("addresses/", AddressListView.as_view(), name="address_list"),
    path("addresses/add/", AddressCreateView.as_view(), name="address_create"),
    path("addresses/<int:pk>/edit/", AddressUpdateView.as_view(), name="address_update"),
    path("addresses/<int:pk>/delete/", AddressDeleteView.as_view(), name="address_delete"),

    # Changement d'e-mail
    path("email-change/", EmailChangeRequestView.as_view(), name="email_change"),
    path("email-change-confirm/<uidb64>/<token>/", EmailChangeConfirmView.as_view(), name="email_change_confirm"),
]

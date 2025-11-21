from django.contrib import admin
from .models import User, Address, EmailChangeRequest

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configuration de l'interface d'administration pour les utilisateurs personnalisés."""

    list_display = (
        "username",
        "email",
        "company_name",
        "is_b2b_verified",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_b2b_verified", "is_staff", "is_active")
    search_fields = ("username", "email", "company_name")
    ordering = ("username",)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Affiche les adresses de carnet dans l'admin."""

    list_display = (
        "user",
        "company_name",
        "contact_name",
        "address1",
        "city",
        "country",
        "type",
        "is_default",
    )
    list_filter = ("type", "country", "is_default")
    search_fields = (
        "company_name",
        "contact_name",
        "address1",
        "city",
        "postcode",
    )
    ordering = ("user", "-is_default")


@admin.register(EmailChangeRequest)
class EmailChangeRequestAdmin(admin.ModelAdmin):
    """Permet de consulter et gérer les demandes de changement d'email."""

    list_display = ("user", "new_email", "created_at", "used")
    list_filter = ("used", "created_at")
    search_fields = ("user__username", "user__email", "new_email")
    ordering = ("-created_at",)

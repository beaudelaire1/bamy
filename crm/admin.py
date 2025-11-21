from django.contrib import admin
from .models import Customer, QuoteRequest


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Configuration de l'interface d'administration pour les clients."""

    list_display = ("client_code", "company", "store_type", "postal_code", "last_name")
    list_filter = ("company",)
    search_fields = ("client_code", "company", "first_name", "last_name", "store_type")
    ordering = ("-created_at", "client_code", "store_type", "postal_code")


# Enregistrement des demandes de devis dans l'admin.  Cette configuration
# permet de voir rapidement qui a envoyé une demande de devis et quand.
@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "company", "created_at")
    list_filter = ("created_at",)
    search_fields = ("email", "company", "first_name", "last_name")
    ordering = ("-created_at",)
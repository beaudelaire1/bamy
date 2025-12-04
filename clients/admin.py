from django.contrib import admin
from .models import Client, UserClientLink


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "settings_currency", "default_pricing_mode", "sales_rep")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(UserClientLink)
class UserClientLinkAdmin(admin.ModelAdmin):
    list_display = ("user", "client", "role", "is_active")
    list_filter = ("role", "is_active")
    search_fields = ("user__email", "client__name")
    autocomplete_fields = ("user", "client")

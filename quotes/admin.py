from django.contrib import admin
from .models import Quote, QuoteItem


class QuoteItemInline(admin.TabularInline):
    model = QuoteItem
    extra = 1
    readonly_fields = ("line_total",)


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "user", "status", "created_at", "validated_at")
    list_filter = ("status", "client")
    date_hierarchy = "created_at"
    inlines = [QuoteItemInline]


@admin.register(QuoteItem)
class QuoteItemAdmin(admin.ModelAdmin):
    list_display = ("quote", "product", "quantity", "unit_price", "line_total")
    list_filter = ("quote", "product")

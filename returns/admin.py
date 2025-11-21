from django.contrib import admin
from .models import ReturnRequest


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ("order_item", "status", "requested_at", "processed_at")
    list_filter = ("status",)
    search_fields = ("order_item__product_title",)
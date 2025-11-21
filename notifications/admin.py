from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "message", "created_at", "read")
    list_filter = ("read",)
    search_fields = ("message", "user__username", "user__email")
    ordering = ("-created_at",)
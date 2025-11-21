from django.contrib import admin
from .models import IntegrationLog, ImportTask


@admin.register(IntegrationLog)
class IntegrationLogAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "status")
    ordering = ("-created_at",)


@admin.register(ImportTask)
class ImportTaskAdmin(admin.ModelAdmin):
    """Configuration d'affichage pour les tâches d'importation."""

    list_display = (
        'id',
        'user',
        'file',
        'status',
        'success_count',
        'failure_count',
        'created_at',
        'completed_at',
    )
    list_filter = ('status', 'user')
    search_fields = ('file', 'user__username', 'status')
    ordering = ('-created_at',)
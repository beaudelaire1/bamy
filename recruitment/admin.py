"""Configuration de l'administration pour l'application de recrutement."""

from django.contrib import admin
from django.utils.html import format_html
from .models import JobPosting, JobApplication


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "published_at", "is_active")
    list_filter = ("is_active", "department")
    search_fields = ("title", "department", "location")


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("job", "name", "email", "created_at", "resume_link", "cover_letter_link")
    list_filter = ("job", "created_at")
    search_fields = ("name", "email", "message")
    readonly_fields = ("resume_link", "cover_letter_link")

    def resume_link(self, obj):
        """Retourne un lien de téléchargement vers le CV du candidat."""
        if obj.resume:
            return format_html(
                '<a href="{}" target="_blank" class="button">Télécharger</a>',
                obj.resume.url,
            )
        return "—"

    resume_link.short_description = "CV"
    resume_link.allow_tags = True

    def cover_letter_link(self, obj):
        """Retourne un lien de téléchargement vers la lettre de motivation."""
        if getattr(obj, "cover_letter", None):
            return format_html(
                '<a href="{}" target="_blank" class="button">Télécharger</a>',
                obj.cover_letter.url,
            )
        return "—"

    cover_letter_link.short_description = "Lettre de motivation"
    cover_letter_link.allow_tags = True
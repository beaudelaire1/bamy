"""Configuration de l'administration pour l'application de recrutement."""

from django.contrib import admin
from .models import JobPosting, JobApplication


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "published_at", "is_active")
    list_filter = ("is_active", "department")
    search_fields = ("title", "department", "location")


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("job", "name", "email", "created_at")
    list_filter = ("job", "created_at")
    search_fields = ("name", "email", "message")
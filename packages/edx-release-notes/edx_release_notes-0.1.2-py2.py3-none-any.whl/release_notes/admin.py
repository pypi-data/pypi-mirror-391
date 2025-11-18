"""Admin configuration for ReleaseNote model."""

from django.contrib import admin

from release_notes.models import ReleaseNote


@admin.register(ReleaseNote)
class ReleaseNoteAdmin(admin.ModelAdmin):
    """Admin settings for managing ReleaseNote entries."""

    list_display = (
        "title",
        "created_by",
        "last_updated_by",
        "published_at",
    )
    search_fields = ("title", "created_by__email", "last_updated_by__email")
    list_filter = ("published_at",)

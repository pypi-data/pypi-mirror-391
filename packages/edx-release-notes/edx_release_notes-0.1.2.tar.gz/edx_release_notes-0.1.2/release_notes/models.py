"""Models for release notes feature."""

from django.contrib.auth import get_user_model
from django.db import models
from model_utils.models import TimeStampedModel

User = get_user_model()


class ReleaseNote(TimeStampedModel):
    """Model to store release note content."""

    title = models.CharField(max_length=255)
    raw_html_content = models.TextField()
    published_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="post_created_by",
    )
    last_updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="post_last_updated_by",
    )

    def __str__(self):
        """Return string representation of the release note."""
        return f"{self.title} - {self.published_at}"

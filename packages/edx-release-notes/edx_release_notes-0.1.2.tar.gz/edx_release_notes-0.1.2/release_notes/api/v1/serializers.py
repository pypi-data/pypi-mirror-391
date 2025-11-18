"""
Serializers for the Release Notes API (v1).
"""

from rest_framework import serializers

from release_notes.models import ReleaseNote


class ReleaseNoteSerializer(serializers.ModelSerializer):
    """
    Serializer used for list/create/update operations.
    """

    created_by = serializers.EmailField(source="created_by.email", read_only=True)
    published_at = serializers.DateTimeField(required=True)

    class Meta:
        model = ReleaseNote
        fields = ["id", "title", "raw_html_content", "published_at", "created_by"]

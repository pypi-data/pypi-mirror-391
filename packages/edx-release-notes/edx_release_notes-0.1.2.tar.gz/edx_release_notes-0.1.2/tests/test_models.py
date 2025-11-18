"""Tests for the ReleaseNote model."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from release_notes.models import ReleaseNote

User = get_user_model()


class ReleaseNoteModelTest(TestCase):
    """Test case for ReleaseNote model."""

    def setUp(self):
        """Set up a user for testing."""
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
        )

    def test_create_release_note(self):
        """Test creating a ReleaseNote instance."""
        release_note = ReleaseNote.objects.create(
            title="Test Release Note",
            raw_html_content="<p>Test content</p>",
            published_at=timezone.now(),
            created_by=self.user,
            last_updated_by=self.user,
        )
        self.assertEqual(
            str(release_note), f"{release_note.title} - {release_note.published_at}"
        )
        self.assertEqual(release_note.title, "Test Release Note")
        self.assertIn("<p>", release_note.raw_html_content)
        self.assertEqual(release_note.created_by.email, "testuser@example.com")
        self.assertEqual(release_note.last_updated_by.email, "testuser@example.com")

    def test_published_at_nullable(self):
        """Test that published_at can be None."""
        release_note = ReleaseNote.objects.create(
            title="No publish date",
            raw_html_content="Content",
            created_by=self.user,
            last_updated_by=self.user,
        )
        self.assertIsNone(release_note.published_at)

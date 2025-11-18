"""
Views for the Release Notes API (v1).
"""

from django.utils import timezone
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from release_notes.api.v1.serializers import ReleaseNoteSerializer
from release_notes.models import ReleaseNote
from release_notes.permissions import CanViewReleaseNotes
from release_notes.toggles import is_release_notes_enabled


class ReleaseNoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ReleaseNote.

    - Read (list, retrieve): allowed for any authenticated user.
    - Write (create, update, destroy): restricted to staff/admin users.

    The viewset sets `created_by` on create and `last_updated_by` on update automatically.
    """

    authentication_classes = (JwtAuthentication, SessionAuthentication)
    serializer_class = ReleaseNoteSerializer
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            queryset = ReleaseNote.objects.all()
        else:
            queryset = ReleaseNote.objects.filter(published_at__lte=timezone.now())
        return queryset.order_by("-published_at")

    def initial(self, request, *args, **kwargs):
        """
        Enforce the feature toggle for release notes early in the request lifecycle.
        If the feature is disabled, raise PermissionDenied for write operations (POST, PUT, DELETE).
        Read operations (GET) are always allowed.
        """
        if request.method != 'GET' and not is_release_notes_enabled():
            raise PermissionDenied("Release notes feature is not enabled.")
        return super().initial(request, *args, **kwargs)

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsAuthenticated, CanViewReleaseNotes]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        Set `created_by` and `last_updated_by` to the request user when creating.
        """
        user = getattr(self.request, "user", None)
        serializer.save(created_by=user, last_updated_by=user)

    def perform_update(self, serializer):
        """
        Update `last_updated_by` to the request user when updating.
        """
        user = getattr(self.request, "user", None)
        serializer.save(last_updated_by=user)

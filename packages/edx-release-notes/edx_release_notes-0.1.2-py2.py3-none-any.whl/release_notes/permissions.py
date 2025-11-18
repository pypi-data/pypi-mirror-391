"""
Custom permissions classes for use with DRF.
"""

from rest_framework.permissions import BasePermission

try:
    from common.djangoapps.student.models import CourseAccessRole
except ImportError:
    CourseAccessRole = None


class CanViewReleaseNotes(BasePermission):
    """
    Custom Permission class for ReleaseNoteViewSet.
    """

    def has_permission(self, request, view):
        """
        Create custom has_permission method.
        """
        user = request.user
        if user.is_staff or user.is_superuser:
            return True
        if CourseAccessRole and CourseAccessRole.objects.filter(user=user).exists():
            return True
        return False

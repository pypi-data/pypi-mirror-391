"""
URL configuration for the Release Notes API (v1).
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from release_notes.api.v1.views import ReleaseNoteViewSet

router = DefaultRouter()
router.register(r"posts", ReleaseNoteViewSet, basename="release_note")

urlpatterns = [
    path("", include(router.urls)),
]

"""
URLs for release_notes.
"""

from django.urls import include, re_path

urlpatterns = [
    re_path(r"^v1/", include("release_notes.api.v1.urls")),
]

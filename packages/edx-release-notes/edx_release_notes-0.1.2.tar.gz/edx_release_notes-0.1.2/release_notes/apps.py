"""
release_notes Django application initialization.
"""

from django.apps import AppConfig


class ReleaseNotesConfig(AppConfig):
    """
    Configuration for the release_notes Django application.
    """

    name = "release_notes"
    plugin_app = {
        "url_config": {
            "lms.djangoapp": {
                "namespace": "release_notes",
                "regex": "^api/release_notes/",
                "relative_path": "urls",
            },
            "cms.djangoapp": {
                "namespace": "release_notes",
                "regex": "^api/release_notes/",
                "relative_path": "urls",
            },
        },
        "settings_config": {
            "lms.djangoapp": {
                "common": {
                    "relative_path": "settings.common",
                },
                "devstack": {
                    "relative_path": "settings.devstack",
                },
                "production": {
                    "relative_path": "settings.production",
                },
            },
            "cms.djangoapp": {
                "common": {
                    "relative_path": "settings.common",
                },
                "devstack": {
                    "relative_path": "settings.devstack",
                },
                "production": {
                    "relative_path": "settings.production",
                },
            },
        },
    }

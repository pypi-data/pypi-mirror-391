"""
Devstack settings for release_notes app.
"""

from .common import plugin_settings as common_plugin_settings


def plugin_settings(settings):
    """
    Devstack settings for release_notes app.

    For now there are no custom devstack settings. Add settings here if we need to
    override common settings.
    """
    common_plugin_settings(settings)

"""
Toggles for release_notes app.
"""

from edx_toggles.toggles import WaffleFlag

# .. toggle_name: release_notes.enable_release_notes
# .. toggle_implementation: WaffleFlag
# .. toggle_default: False
# .. toggle_description: Waffle flag to enable the release notes feature
# .. toggle_use_cases: temporary
# .. toggle_creation_date: 2025-10-10
# .. toggle_target_removal_date: 2026-04-10
# .. toggle_tickets: TNL2-386
ENABLE_RELEASE_NOTES = WaffleFlag(
    "release_notes.enable_release_notes",
    module_name=__name__,
    log_prefix="release_notes",
)


def is_release_notes_enabled():
    """
    Return Waffle flag for enabling the release notes feature.
    """
    return ENABLE_RELEASE_NOTES.is_enabled()

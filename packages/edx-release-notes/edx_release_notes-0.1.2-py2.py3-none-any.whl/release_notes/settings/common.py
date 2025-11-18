"""
release_notes common settings.
"""


def plugin_settings(settings):
    """
    Common settings for release_notes application.

    default env settings variables
    settings.DEFAULT_ENV_VARIABLE = 'TEST_DEFAULT_VALUE'

    get settings from env_tokens dictionary
    settings.ENV_TOKENS_ENV_VARIABLE = env_tokens.get('ENV_TOKENS_ENV_VARIABLE', '')
    """
    env_tokens = getattr(settings, 'ENV_TOKENS', {})  # pylint: disable=unused-variable

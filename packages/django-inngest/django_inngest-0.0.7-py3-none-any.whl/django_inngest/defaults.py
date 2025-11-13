"""
Configuration for django_inngest Inngest integration.

This module provides a centralized way to manage Inngest settings
with sensible defaults that can be overridden in Django settings.

To override any setting, add it to your Django settings.py:
    DJANGO_INNGEST_APP_ID = "my-django-project"
    DJANGO_INNGEST_IS_PRODUCTION = False
    INNGEST_EVENT_KEY = None
    INNGEST_SIGNING_KEY = None
"""

from django.conf import settings

# Default settings
DEFAULTS = {
    "DJANGO_INNGEST_APP_ID": "my-django-project",
    "DJANGO_INNGEST_IS_PRODUCTION": True,
    "INNGEST_EVENT_KEY": None,
    "INNGEST_SIGNING_KEY": None,
    "DJANGO_INNGEST_CLIENT_LOGGER": "gunicorn",
    "DJANGO_INNGEST_INACTIVE_FUNCTION_IDS": [],
    "DJANGO_INNGEST_AUTO_DISCOVER_FUNCTIONS": True,
    "DJANGO_INNGEST_SERVE_PATH": "api/inngest",
    "DJANGO_INNGEST_API_BASE_URL": None,
}


def get_django_inngest_setting(name):
    """
    Get a django_inngest setting from Django settings or return the default.

    Args:
        name: The setting name (e.g., 'INNGEST_EVENT_KEY')

    Returns:
        The setting value from Django settings, or the default if not set
    """
    return getattr(settings, name, DEFAULTS.get(name))


# Convenience accessors
INNGEST_EVENT_KEY = get_django_inngest_setting("INNGEST_EVENT_KEY")
INNGEST_SIGNING_KEY = get_django_inngest_setting("INNGEST_SIGNING_KEY")
DJANGO_INNGEST_APP_ID = get_django_inngest_setting("DJANGO_INNGEST_APP_ID")
DJANGO_INNGEST_IS_PRODUCTION = get_django_inngest_setting(
    "DJANGO_INNGEST_IS_PRODUCTION"
)
DJANGO_INNGEST_CLIENT_LOGGER = get_django_inngest_setting(
    "DJANGO_INNGEST_CLIENT_LOGGER"
)
DJANGO_INNGEST_AUTO_DISCOVER_FUNCTIONS = get_django_inngest_setting(
    "DJANGO_INNGEST_AUTO_DISCOVER_FUNCTIONS"
)
DJANGO_INNGEST_INACTIVE_FUNCTION_IDS = get_django_inngest_setting(
    "DJANGO_INNGEST_INACTIVE_FUNCTION_IDS"
)
DJANGO_INNGEST_SERVE_PATH = get_django_inngest_setting("DJANGO_INNGEST_SERVE_PATH")
DJANGO_INNGEST_API_BASE_URL = get_django_inngest_setting("DJANGO_INNGEST_API_BASE_URL")

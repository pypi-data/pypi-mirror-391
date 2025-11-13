"""
Basic tests for django-inngest package.
"""

import pytest  # noqa: F401


def test_import_django_inngest():
    """Test that django_inngest can be imported."""
    import django_inngest  # noqa: F401


def test_import_inngest_client():
    """Test that the inngest_client can be imported."""
    from django_inngest import inngest_client  # noqa: F401

    assert inngest_client is not None


def test_import_discover_functions():
    """Test that discover_inngest_functions can be imported."""
    from django_inngest import discover_inngest_functions  # noqa: F401

    assert discover_inngest_functions is not None


def test_django_setup():
    """Test that Django can be set up with the package installed."""
    import django  # noqa: F401
    from django.conf import settings

    assert settings.configured

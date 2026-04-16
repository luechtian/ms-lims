"""Smoke test: Django is properly configured."""

import django
from django.conf import settings


def test_django_version():
    """Django 6.0.x ist aktiv."""
    assert django.VERSION[:2] == (6, 0)


def test_settings_loaded():
    """Config-Modul lädt sauber, Zeitzone ist gesetzt."""
    assert settings.TIME_ZONE == "Europe/Berlin"
    assert settings.LANGUAGE_CODE == "de-de"
    assert settings.USE_TZ is True


def test_sqlite_wal_mode_configured():
    """PRAGMA-Tuning ist in den DB-Optionen gesetzt."""
    db_opts = settings.DATABASES["default"]["OPTIONS"]
    assert db_opts["transaction_mode"] == "IMMEDIATE"
    assert "journal_mode=WAL" in db_opts["init_command"]

"""
Django settings for the Assignment 3 chatbot project.

The project has no web views. Django provides the ORM that stores
ChatterBot's conversation data and the management commands that run
the terminal client.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Only used for Django's signing features, which this project does not expose.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-not-for-production")

DEBUG = os.environ.get("DJANGO_DEBUG", "False") == "True"

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    # ChatterBot's Django models (Statement, Tag) used by DjangoStorageAdapter
    "chatterbot.ext.django_chatterbot",
    "chatbot",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

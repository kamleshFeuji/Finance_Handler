"""HTTP loopback development only; not deployment settings."""
import os

from .base import *  # noqa: F403

DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
LOCAL_SINGLE_USER = True

"""PostgreSQL test configuration, using a separate local test role."""
import os

from .base import *  # noqa: F403

DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
DATABASES["default"]["USER"] = os.getenv("TEST_DB_USER", "savequest_test")  # noqa: F405
DATABASES["default"]["PASSWORD"] = os.getenv("TEST_DB_PASSWORD", "")  # noqa: F405
DATABASES["default"]["TEST"] = {  # noqa: F405
    "NAME": os.getenv("TEST_DB_NAME", "test_savequest"),
}
if DATABASES["default"]["TEST"]["NAME"] == DATABASES["default"]["NAME"]:  # noqa: F405
    raise ValueError("The test database must differ from the development database.")
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
LOCAL_SINGLE_USER = True

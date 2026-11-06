from unittest.mock import patch

from django.db import OperationalError
from django.test import SimpleTestCase
from django.urls import reverse


class HealthTests(SimpleTestCase):
    def test_connected_database_returns_readiness_without_secrets(self):
        with patch("config.views.connection") as database:
            response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["database"], "connected")
        database.cursor.return_value.__enter__.return_value.execute.assert_called_once_with(
            "SELECT 1"
        )
        self.assertIn("no-store", response.headers["Cache-Control"])

    def test_database_error_returns_503_and_does_not_expose_exception(self):
        with patch("config.views.connection") as database:
            database.cursor.side_effect = OperationalError("sensitive connection information")
            response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["database"], "unavailable")
        self.assertNotContains(response, "sensitive", status_code=503)

    def test_health_is_read_only(self):
        response = self.client.post(reverse("health"))
        self.assertEqual(response.status_code, 405)

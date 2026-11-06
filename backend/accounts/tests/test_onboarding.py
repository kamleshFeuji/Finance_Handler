import json
from decimal import Decimal
from unittest.mock import patch

from django.db import OperationalError
from django.test import Client, SimpleTestCase, override_settings

from accounts.serializers import ProfileSerializer


class ProfileValidationTests(SimpleTestCase):
    def test_every_question_can_be_skipped(self):
        serializer = ProfileSerializer(data={})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_zero_is_distinct_from_unknown(self):
        serializer = ProfileSerializer(data={"expected_monthly_income": "0", "essential_monthly_expenses": None})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["expected_monthly_income"], Decimal("0.00"))
        self.assertIsNone(serializer.validated_data["essential_monthly_expenses"])

    def test_invalid_money_is_rejected(self):
        for amount in ("-1", "0.001", "NaN", "Infinity", "1000000000000", "hello"):
            with self.subTest(amount=amount):
                serializer = ProfileSerializer(data={"existing_savings_estimate": amount})
                self.assertFalse(serializer.is_valid())

    def test_invalid_choices_and_client_owners_are_rejected(self):
        for data in ({"income_type": "bogus"}, {"priority": "bogus"}, {"user": 2}, []):
            with self.subTest(data=data):
                self.assertFalse(ProfileSerializer(data=data).is_valid())


@override_settings(ALLOWED_HOSTS=["localhost", "example.com"])
class ProfileAPITests(SimpleTestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True, HTTP_HOST="localhost")

    def put(self, data, token=None):
        return self.client.put("/api/v1/profile/", json.dumps(data), content_type="application/json", **({"HTTP_X_CSRFTOKEN": token} if token else {}))

    def token(self):
        return self.client.get("/api/v1/csrf/").json()["csrf_token"]

    @patch("accounts.views.load_profile", return_value=None)
    def test_get_before_onboarding_returns_no_profile_without_creating_one(self, load):
        response = self.client.get("/api/v1/profile/")
        self.assertEqual(response.json(), {"profile": None})
        self.assertIn("no-store", response.headers["Cache-Control"])

    @patch("accounts.views.save_profile")
    def test_anonymous_write_requires_csrf(self, save):
        self.assertEqual(self.put({}).status_code, 403)
        save.assert_not_called()

    @patch("accounts.views.save_profile", return_value={"nickname": "Alex"})
    def test_valid_csrf_allows_single_user_save_without_login(self, save):
        response = self.put({"nickname": "Alex"}, self.token())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["profile"]["nickname"], "Alex")

    @patch("accounts.views.save_profile")
    def test_invalid_values_do_not_reach_persistence(self, save):
        response = self.put({"expected_monthly_income": "-5"}, self.token())
        self.assertEqual(response.status_code, 400)
        self.assertIn("expected_monthly_income", response.json()["errors"])
        save.assert_not_called()

    def test_malformed_json_returns_clear_error(self):
        response = self.client.put("/api/v1/profile/", "{", content_type="application/json", HTTP_X_CSRFTOKEN=self.token())
        self.assertEqual(response.status_code, 400)

    @patch("accounts.views.load_profile", side_effect=OperationalError("private details"))
    def test_database_failure_does_not_leak_details(self, load):
        response = self.client.get("/api/v1/profile/")
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private details", response.content.decode())

    @patch("accounts.views.load_profile")
    def test_remote_clients_and_unexpected_hosts_are_denied(self, load):
        self.assertEqual(self.client.get("/api/v1/profile/", REMOTE_ADDR="192.168.1.20").status_code, 403)
        self.assertEqual(self.client.get("/api/v1/profile/", HTTP_HOST="example.com").status_code, 403)
        load.assert_not_called()

    @override_settings(LOCAL_SINGLE_USER=False)
    def test_feature_is_disabled_outside_explicit_local_mode(self):
        self.assertEqual(self.client.get("/api/v1/profile/").status_code, 403)

    def test_foreign_origin_cannot_write_even_with_a_token(self):
        response = self.client.put("/api/v1/profile/", "{}", content_type="application/json", HTTP_X_CSRFTOKEN=self.token(), HTTP_ORIGIN="https://example.com")
        self.assertEqual(response.status_code, 403)

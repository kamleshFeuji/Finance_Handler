import json
import uuid
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.test import Client, SimpleTestCase, override_settings
from django.utils import timezone

from finances.serializers import IncomeCreate, IncomeUpdate
from finances.services import IncomeError, month_bounds


def payload(**changes):
    return {"amount": "1500.25", "source": "freelance", "received_on": timezone.localdate().isoformat(), "request_key": str(uuid.uuid4()), **changes}


class IncomeValidationTests(SimpleTestCase):
    def test_valid_irregular_income_uses_decimal_and_dates(self):
        serializer = IncomeCreate(data=payload())
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["amount"], Decimal("1500.25"))
        self.assertEqual(serializer.validated_data["received_on"], timezone.localdate())

    def test_amount_is_required_positive_finite_and_has_two_decimal_places(self):
        for value in ("0", "-1", "NaN", "Infinity", "0.001", "1000000000000", ""):
            with self.subTest(amount=value):
                self.assertFalse(IncomeCreate(data=payload(amount=value)).is_valid())

    def test_future_income_is_not_recorded_as_actual(self):
        serializer = IncomeCreate(data=payload(received_on=(timezone.localdate() + timedelta(days=1)).isoformat()))
        self.assertFalse(serializer.is_valid())
        self.assertIn("received_on", serializer.errors)

    def test_ownership_keys_and_unknown_fields_cannot_be_supplied(self):
        for extra in ({"user": 2}, {"version": 5}, {"source": "bogus"}, {"request_key": "bogus"}, {"label": "x" * 101}):
            with self.subTest(extra=extra):
                self.assertFalse(IncomeCreate(data=payload(**extra)).is_valid())

    def test_edit_requires_version_and_all_required_fields(self):
        values = payload()
        values.pop("request_key")
        self.assertFalse(IncomeUpdate(data=values).is_valid())
        serializer = IncomeUpdate(data={**values, "expected_version": 1})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_calendar_month_bounds_cover_leap_year_and_year_end(self):
        self.assertEqual(month_bounds("2024-02"), (date(2024, 2, 1), date(2024, 2, 29)))
        self.assertEqual(month_bounds("2026-12"), (date(2026, 12, 1), date(2026, 12, 31)))

    def test_invalid_months_are_rejected(self):
        for value in ("2026-1", "2026-13", "0000-01", "all", "2026-11-01"):
            with self.subTest(value=value), self.assertRaises(IncomeError):
                month_bounds(value)


@override_settings(ALLOWED_HOSTS=["localhost"])
class IncomeAPITests(SimpleTestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True, HTTP_HOST="localhost")

    def token(self):
        return self.client.get("/api/v1/csrf/").json()["csrf_token"]

    def test_all_mutations_require_csrf_without_login(self):
        for method, path in (("post", "/api/v1/income/"), ("put", "/api/v1/income/1/"), ("delete", "/api/v1/income/1/")):
            with self.subTest(method=method):
                response = getattr(self.client, method)(path, "{}", content_type="application/json")
                self.assertEqual(response.status_code, 403)

    @patch("finances.views.services.create_income")
    def test_invalid_entry_does_not_reach_persistence(self, create):
        response = self.client.post("/api/v1/income/", json.dumps(payload(amount="-1")), content_type="application/json", HTTP_X_CSRFTOKEN=self.token())
        self.assertEqual(response.status_code, 400)
        self.assertIn("amount", response.json()["errors"])
        create.assert_not_called()

    @patch("finances.views.services.create_income")
    def test_malformed_json_is_reported(self, create):
        response = self.client.post("/api/v1/income/", "{", content_type="application/json", HTTP_X_CSRFTOKEN=self.token())
        self.assertEqual(response.status_code, 400)
        create.assert_not_called()

    @patch("finances.views.services.list_income", return_value=([], {"month": "2026-11", "total": "0.00", "count": 0, "page": 1, "pages": 1}))
    def test_empty_month_has_explicit_zero_total_and_is_not_cached(self, listing):
        response = self.client.get("/api/v1/income/?month=2026-11&page=1")
        self.assertEqual(response.json()["total"], "0.00")
        self.assertEqual(response.json()["results"], [])
        self.assertIn("no-store", response.headers["Cache-Control"])
        listing.assert_called_once_with("2026-11", "1")

    @patch("finances.views.services.list_income", side_effect=IncomeError("Save your starting point first.", 409))
    def test_missing_profile_has_actionable_error(self, listing):
        response = self.client.get("/api/v1/income/")
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["message"], "Save your starting point first.")

    @patch("finances.views.services.list_income")
    def test_remote_access_is_denied(self, listing):
        self.assertEqual(self.client.get("/api/v1/income/", REMOTE_ADDR="192.168.1.10").status_code, 403)
        listing.assert_not_called()

    def test_foreign_origin_cannot_record_income(self):
        response = self.client.post("/api/v1/income/", json.dumps(payload()), content_type="application/json", HTTP_X_CSRFTOKEN=self.token(), HTTP_ORIGIN="https://example.com")
        self.assertEqual(response.status_code, 403)

import json
import uuid
from datetime import timedelta
from unittest.mock import patch

from django.test import Client, SimpleTestCase, override_settings
from django.utils import timezone

from finances.expense_serializers import CategoryInput, ExpenseCreate, ExpenseUpdate


def payload(**changes):
    return {"amount": "250.25", "category": 1, "is_essential": True, "spent_on": timezone.localdate().isoformat(), "request_key": str(uuid.uuid4()), **changes}


class ExpenseValidationTests(SimpleTestCase):
    def test_valid_money_and_explicit_classification(self):
        serializer = ExpenseCreate(data=payload(is_essential=False))
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertFalse(serializer.validated_data["is_essential"])

    def test_invalid_money_and_future_dates_are_rejected(self):
        for value in ("0", "-1", "NaN", "Infinity", "1.001", "1000000000000"):
            with self.subTest(amount=value):
                self.assertFalse(ExpenseCreate(data=payload(amount=value)).is_valid())
        self.assertFalse(ExpenseCreate(data=payload(spent_on=(timezone.localdate() + timedelta(days=1)).isoformat())).is_valid())

    def test_client_owners_and_invalid_categories_are_rejected(self):
        for values in ({"user": 4}, {"category": 0}, {"category": "foreign"}, {"is_essential": None}):
            with self.subTest(values=values):
                self.assertFalse(ExpenseCreate(data=payload(**values)).is_valid())

    def test_edit_requires_a_version(self):
        data = payload()
        data.pop("request_key")
        self.assertFalse(ExpenseUpdate(data=data).is_valid())
        self.assertTrue(ExpenseUpdate(data={**data, "expected_version": 1}).is_valid())

    def test_category_names_are_trimmed_and_whitespace_normalized(self):
        serializer = CategoryInput(data={"name": "  Pet   care ", "default_essential": False})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["name"], "Pet care")
        self.assertFalse(CategoryInput(data={"name": "   "}).is_valid())


@override_settings(ALLOWED_HOSTS=["localhost"])
class ExpenseAPITests(SimpleTestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True, HTTP_HOST="localhost")

    def token(self):
        return self.client.get("/api/v1/csrf/").json()["csrf_token"]

    def test_expense_and_category_writes_require_csrf(self):
        for method, path in (("post", "/api/v1/expenses/"), ("put", "/api/v1/expenses/1/"), ("delete", "/api/v1/expenses/1/"), ("post", "/api/v1/expense-categories/"), ("put", "/api/v1/expense-categories/1/")):
            with self.subTest(path=path, method=method):
                self.assertEqual(getattr(self.client, method)(path, "{}", content_type="application/json").status_code, 403)

    @patch("finances.views.expense_services.create_expense")
    def test_invalid_expense_never_reaches_persistence(self, create):
        response = self.client.post("/api/v1/expenses/", json.dumps(payload(amount="-1")), content_type="application/json", HTTP_X_CSRFTOKEN=self.token())
        self.assertEqual(response.status_code, 400)
        self.assertIn("amount", response.json()["errors"])
        create.assert_not_called()

    @patch("finances.views.expense_services.overview", return_value={"income": "0.00", "expenses": "10.00", "remaining": "-10.00"})
    def test_overview_passes_month_and_returns_decimal_strings_without_caching(self, overview):
        response = self.client.get("/api/v1/overview/?month=2026-11")
        self.assertEqual(response.json()["remaining"], "-10.00")
        self.assertIn("no-store", response.headers["Cache-Control"])
        overview.assert_called_once_with("2026-11")

    @patch("finances.views.expense_services.list_categories")
    def test_remote_categories_are_denied(self, listing):
        self.assertEqual(self.client.get("/api/v1/expense-categories/", REMOTE_ADDR="192.168.1.10").status_code, 403)
        listing.assert_not_called()

    def test_foreign_origin_cannot_write(self):
        response = self.client.post("/api/v1/expenses/", json.dumps(payload()), content_type="application/json", HTTP_X_CSRFTOKEN=self.token(), HTTP_ORIGIN="https://example.com")
        self.assertEqual(response.status_code, 403)

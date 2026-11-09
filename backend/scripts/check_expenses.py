"""Check actual PostgreSQL expense/overview behavior using rolled-back fictional owners."""
import json
import os
import sys
import uuid
from datetime import timedelta
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
import django
django.setup()

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import Client
from django.utils import timezone
from accounts.models import User
from accounts.services import save_profile
from finances.expense_serializers import ExpenseCreate
from finances.expense_services import create_expense
from finances.models import ExpenseCategory, ExpenseChange, ExpenseEntry


def run():
    local_name, other_name = (f"_expense_check_{uuid.uuid4().hex}" for _ in range(2))
    with transaction.atomic(), patch("accounts.services.LOCAL_USERNAME", local_name):
        profile = save_profile({"nickname": "Fictional expense check", "expected_monthly_income": "99999.00", "essential_monthly_expenses": "88888.00"})
        client = Client(enforce_csrf_checks=True, HTTP_HOST="localhost")
        token = client.get("/api/v1/csrf/").json()["csrf_token"]
        today = timezone.localdate()
        month = today.strftime("%Y-%m")
        def write(method, path, data):
            return getattr(client, method)(path, json.dumps(data), content_type="application/json", HTTP_X_CSRFTOKEN=token)
        def categories():
            return client.get("/api/v1/expense-categories/").json()["results"]
        def totals(page=1):
            response = client.get(f"/api/v1/expenses/?month={month}&page={page}")
            assert response.status_code == 200
            return response.json()
        def overview():
            response = client.get(f"/api/v1/overview/?month={month}")
            assert response.status_code == 200
            return response.json()
        def record(amount, category, essential, date=None):
            data = {"amount": amount, "category": category, "is_essential": essential, "spent_on": date or today.isoformat(), "request_key": str(uuid.uuid4())}
            response = write("post", "/api/v1/expenses/", data)
            assert response.status_code == 201, response.status_code
            return response.json()["entry"], data
        choices = categories()
        assert len(choices) == 11
        groceries = next(category for category in choices if category["name"] == "Food and groceries")
        entertainment = next(category for category in choices if category["name"] == "Entertainment")
        assert groceries["default_essential"] is True
        assert totals()["total"] == "0.00" and overview()["income"] == "0.00"
        first, first_data = record("100.25", groceries["id"], True)
        second, second_data = record("40.10", entertainment["id"], False)
        assert overview()["remaining"] == "-140.35"  # Expenses above zero income are allowed.
        assert write("post", "/api/v1/expenses/", first_data).status_code == 200
        assert write("post", "/api/v1/expenses/", {**first_data, "amount": "101.00"}).status_code == 409
        previous = (today.replace(day=1) - timedelta(days=1)).isoformat()
        record("1.01", groceries["id"], True, previous)
        for _ in range(26):
            record("0.01", entertainment["id"], False)
        assert totals()["total"] == "140.61" and totals()["count"] == 28
        assert totals()["essential"] == "100.25" and totals()["optional"] == "40.36"
        assert len(totals()["results"]) == 25 and len(totals(2)["results"]) == 3
        assert sum(Decimal(row['total']) for row in totals()['categories']) == Decimal('140.61')
        assert write("post", "/api/v1/income/", {"amount": "500.00", "source": "allowance", "received_on": today.isoformat(), "request_key": str(uuid.uuid4())}).status_code == 201
        assert overview()["remaining"] == "359.39"
        # Changing a category's default never rewrites historical classification.
        category_path = f"/api/v1/expense-categories/{entertainment['id']}/"
        changed = write("put", category_path, {"name": entertainment["name"], "default_essential": True, "is_archived": False, "expected_version": 1})
        assert changed.status_code == 200
        assert totals()["optional"] == "40.36"
        record("5.00", entertainment["id"], False)
        assert write("put", category_path, {"name": entertainment["name"], "default_essential": True, "is_archived": True, "expected_version": 2}).status_code == 200
        assert totals()["total"] == "145.61"
        assert write("post", "/api/v1/expenses/", {**second_data, "request_key": str(uuid.uuid4())}).status_code == 400
        second_path = f"/api/v1/expenses/{second['id']}/"
        edit = {"amount": "45.10", "category": entertainment["id"], "is_essential": False, "spent_on": today.isoformat(), "expected_version": 1}
        assert write("put", second_path, edit).status_code == 200  # Existing archived category may remain.
        assert write("put", second_path, edit).status_code == 409
        assert write("put", second_path, {**edit, "category": groceries["id"], "is_essential": True, "expected_version": 2}).status_code == 200
        assert totals()["essential"] == "145.35" and totals()["optional"] == "5.26"
        assert write("delete", second_path, {"expected_version": 2}).status_code == 409
        assert write("delete", second_path, {"expected_version": 3}).status_code == 200
        assert totals()["total"] == "105.51" and overview()["remaining"] == "394.49"
        assert client.get(second_path).status_code == 404
        assert write("post", "/api/v1/expenses/", second_data).status_code == 409
        assert ExpenseChange.objects.filter(entry_id=second["id"]).count() == 4
        assert write("put", category_path, {"name": entertainment["name"], "default_essential": True, "is_archived": False, "expected_version": 3}).status_code == 200
        custom = write("post", "/api/v1/expense-categories/", {"name": "  Pet  care ", "default_essential": True})
        assert custom.status_code == 201 and custom.json()["category"]["name"] == "Pet care"
        assert write("post", "/api/v1/expense-categories/", {"name": "pet care"}).status_code == 409
        assert write("put", category_path, {"name": "Experiences", "default_essential": True, "is_archived": False, "expected_version": 4}).status_code == 200
        save_profile({})
        assert not ExpenseCategory.objects.filter(user=profile.user, name="Entertainment").exists()
        assert ExpenseCategory.objects.filter(user=profile.user).count() == 12
        other = User.objects.create_user(username=other_name, password=None)
        foreign_category = ExpenseCategory.objects.create(user=other, name="Private category", normalized_name="private category")
        foreign = ExpenseEntry.objects.create(user=other, category=foreign_category, amount="999.00", is_essential=True, spent_on=today, creation_fingerprint="0" * 64)
        assert client.get(f"/api/v1/expenses/{foreign.pk}/").status_code == 404
        assert write("delete", f"/api/v1/expenses/{foreign.pk}/", {"expected_version": 1}).status_code == 404
        assert write("post", "/api/v1/expenses/", {**first_data, "category": foreign_category.pk, "request_key": str(uuid.uuid4())}).status_code == 400
        assert write("put", f"/api/v1/expense-categories/{foreign_category.pk}/", {"name": "No", "default_essential": False, "is_archived": True, "expected_version": 1}).status_code == 404
        assert foreign_category.pk not in [category["id"] for category in categories()]
        assert totals()["total"] == "105.51"
        wrong_owner = ExpenseEntry(user=profile.user, category=foreign_category, amount="1.00", is_essential=True, spent_on=today, creation_fingerprint="0" * 64)
        try:
            wrong_owner.full_clean()
        except ValidationError:
            pass
        else:
            raise AssertionError("Model accepted another owner's category")
        try:
            with transaction.atomic():
                ExpenseEntry.objects.filter(pk=first["id"]).update(amount="-1")
        except IntegrityError:
            pass
        else:
            raise AssertionError("Database accepted a negative expense")
        key = str(uuid.uuid4())
        serializer = ExpenseCreate(data={**first_data, "request_key": key})
        serializer.is_valid(raise_exception=True)
        with patch("finances.expense_services.ExpenseChange.objects.create", side_effect=RuntimeError("fictional audit failure")):
            try:
                create_expense(serializer.validated_data)
            except RuntimeError:
                pass
            else:
                raise AssertionError("Audit failure was ignored")
        assert not ExpenseEntry.objects.filter(user=profile.user, request_key=key).exists()
        assert write("post", "/api/v1/expenses/", {**first_data, "spent_on": (today + timedelta(days=1)).isoformat(), "request_key": str(uuid.uuid4())}).status_code == 400
        transaction.set_rollback(True)
    assert not User.objects.filter(username__in=[local_name, other_name]).exists()
    print("PostgreSQL expense checks passed: categories, archives/restores, ownership, exact monthly/overview totals, pagination, edits/deletes, retries, classification snapshots and atomic audits. Fictional records rolled back; personal data unchanged.")


if __name__ == "__main__":
    run()

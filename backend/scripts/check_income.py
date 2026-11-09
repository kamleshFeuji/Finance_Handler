"""PostgreSQL income checks with temporary fictional owners; all writes roll back.

This process-only owner override never changes the running app's owner or profile.
"""
import json
import os
import sys
import uuid
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
import django
django.setup()

from django.db import IntegrityError, transaction
from django.test import Client
from django.utils import timezone

from accounts.models import User
from accounts.services import save_profile
from finances.models import IncomeChange, IncomeEntry
from finances.serializers import IncomeCreate
from finances.services import create_income


def run():
    test_name = f"_income_check_{uuid.uuid4().hex}"
    other_name = f"_other_check_{uuid.uuid4().hex}"
    with transaction.atomic(), patch("accounts.services.LOCAL_USERNAME", test_name):
        profile = save_profile({"nickname": "Fictional income check", "expected_monthly_income": "99999.00"})
        client = Client(enforce_csrf_checks=True, HTTP_HOST="localhost")
        token = client.get("/api/v1/csrf/").json()["csrf_token"]
        today = timezone.localdate()
        month = today.strftime("%Y-%m")
        previous = (today.replace(day=1) - timedelta(days=1)).isoformat()

        def write(method, path, data):
            return getattr(client, method)(path, json.dumps(data), content_type="application/json", HTTP_X_CSRFTOKEN=token)

        def listing(page=1):
            result = client.get(f"/api/v1/income/?month={month}&page={page}")
            assert result.status_code == 200, result.status_code
            return result.json()

        def record(amount, date=None, key=None):
            data = {"amount": amount, "source": "freelance", "received_on": date or today.isoformat(), "request_key": key or str(uuid.uuid4())}
            response = write("post", "/api/v1/income/", data)
            assert response.status_code == 201, response.status_code
            return response.json()["entry"], data

        assert listing()["total"] == "0.00"  # Onboarding estimates never count.
        first, payload = record("100.25")
        duplicate = write("post", "/api/v1/income/", payload)
        assert duplicate.status_code == 200
        assert duplicate.json()["entry"]["id"] == first["id"]
        assert IncomeEntry.objects.filter(user=profile.user).count() == 1
        assert IncomeChange.objects.filter(entry_id=first["id"]).count() == 1
        assert write("post", "/api/v1/income/", {**payload, "amount": "200.00"}).status_code == 409
        record("9.99", previous)
        for _ in range(26):
            record("1.01")
        assert listing()["total"] == "126.51"
        assert listing()["count"] == 27
        assert len(listing()["results"]) == 25
        assert len(listing(2)["results"]) == 2
        previous_month = client.get(f"/api/v1/income/?month={previous[:7]}").json()
        assert previous_month["total"] == "9.99"
        other = User.objects.create_user(username=other_name, password=None)
        foreign = IncomeEntry.objects.create(user=other, amount="777.00", source="other", received_on=today, creation_fingerprint="0" * 64)
        assert client.get(f"/api/v1/income/{foreign.pk}/").status_code == 404
        assert write("delete", f"/api/v1/income/{foreign.pk}/", {"expected_version": 1}).status_code == 404
        assert listing()["total"] == "126.51"
        path = f"/api/v1/income/{first['id']}/"
        edit = {"amount": "150.25", "source": "salary", "received_on": today.isoformat(), "label": "Fictional edit", "expected_version": 1}
        updated = write("put", path, edit)
        assert updated.status_code == 200
        assert updated.json()["entry"]["version"] == 2
        assert write("put", path, edit).status_code == 409
        assert listing()["total"] == "176.51"
        assert write("delete", path, {"expected_version": 1}).status_code == 409
        assert write("delete", path, {"expected_version": 2}).status_code == 200
        assert listing()["total"] == "26.26"
        assert listing()["count"] == 26
        assert client.get(path).status_code == 404
        assert write("post", "/api/v1/income/", payload).status_code == 409
        assert IncomeChange.objects.filter(entry_id=first["id"]).count() == 3
        audit = IncomeChange.objects.get(entry_id=first["id"], action="updated")
        assert audit.before["amount"] == "100.25" and audit.after["amount"] == "150.25"
        future = (today + timedelta(days=1)).isoformat()
        assert write("post", "/api/v1/income/", {**payload, "received_on": future, "request_key": str(uuid.uuid4())}).status_code == 400
        for query in ("month=invalid", f"month={month}&page=0", f"month={month}&page=999"):
            assert client.get(f"/api/v1/income/?{query}").status_code == 400
        try:
            with transaction.atomic():
                IncomeEntry.objects.filter(pk=first["id"]).update(amount="-1")
        except IntegrityError:
            pass
        else:
            raise AssertionError("Negative income was accepted by PostgreSQL")
        atomic_key = str(uuid.uuid4())
        atomic_input = IncomeCreate(data={**payload, "amount": "3.14", "request_key": atomic_key})
        atomic_input.is_valid(raise_exception=True)
        with patch("finances.services.IncomeChange.objects.create", side_effect=RuntimeError("fictional audit failure")):
            try:
                create_income(atomic_input.validated_data)
            except RuntimeError:
                pass
            else:
                raise AssertionError("Audit failure did not propagate")
        assert not IncomeEntry.objects.filter(user=profile.user, request_key=atomic_key).exists()
        transaction.set_rollback(True)
    assert not User.objects.filter(username__in=[test_name, other_name]).exists()
    print("PostgreSQL income checks passed: exact totals, month filtering, pagination, retry safety, edit/delete, version conflicts, ownership, audit atomicity and constraints. All fictional records rolled back; personal data unchanged.")


if __name__ == "__main__":
    run()

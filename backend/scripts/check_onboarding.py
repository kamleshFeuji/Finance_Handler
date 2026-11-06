"""Real PostgreSQL onboarding smoke check. Fictional writes are rolled back.

Run only before the first local profile is created. Never edits an existing profile.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

import django
django.setup()

from django.db import IntegrityError, transaction
from django.test import Client

from accounts.models import User, UserFinancialProfile
from accounts.services import LOCAL_USERNAME, LocalOwnerConflict, save_profile


def run():
    with transaction.atomic():
        if User.objects.filter(username=LOCAL_USERNAME).exists():
            raise RuntimeError("Local account already exists. Leave its data untouched; use the isolated test database instead.")
        client = Client(enforce_csrf_checks=True, HTTP_HOST="localhost")
        assert client.get("/api/v1/profile/").json() == {"profile": None}
        token = client.get("/api/v1/csrf/").json()["csrf_token"]
        payload = {"nickname": "Fictional test user", "income_type": "freelance", "expected_monthly_income": "0.00", "existing_savings_estimate": "100.25"}
        def put(data):
            return client.put("/api/v1/profile/", json.dumps(data), content_type="application/json", HTTP_X_CSRFTOKEN=token)
        response = put(payload)
        assert response.status_code == 200, response.status_code
        saved_at = response.json()["profile"]["onboarding_completed_at"]
        assert put(payload).status_code == 200
        assert UserFinancialProfile.objects.count() == 1
        profile = client.get("/api/v1/profile/").json()["profile"]
        assert profile["expected_monthly_income"] == "0.00"
        assert profile["essential_monthly_expenses"] is None
        assert profile["existing_savings_estimate"] == "100.25"
        assert profile["onboarding_completed_at"] == saved_at
        assert not User.objects.get(username=LOCAL_USERNAME).has_usable_password()
        assert put({"expected_monthly_income": "-1"}).status_code == 400
        assert put({"user": 999}).status_code == 400
        assert put({}).status_code == 200
        assert client.get("/api/v1/profile/").json()["profile"]["expected_monthly_income"] is None
        try:
            with transaction.atomic():
                UserFinancialProfile.objects.update(existing_savings_estimate="-1")
        except IntegrityError:
            pass
        else:
            raise AssertionError("Database accepted a negative estimate")
        owner = User.objects.get(username=LOCAL_USERNAME)
        owner.set_password("fictional-test-only")
        owner.save()
        try:
            save_profile({})
        except LocalOwnerConflict:
            pass
        else:
            raise AssertionError("Existing usable account was overwritten")
        transaction.set_rollback(True)
    assert not User.objects.filter(username=LOCAL_USERNAME).exists()
    print("PostgreSQL onboarding checks passed: CSRF, create/read/update, retries, unknown vs zero, ownership, constraints, and rollback. No test profile retained.")


if __name__ == "__main__":
    run()

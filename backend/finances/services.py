import calendar
import hashlib
import json
import re
from datetime import date
from decimal import Decimal

from django.core.paginator import EmptyPage, Paginator
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from accounts.models import User
from accounts.services import LocalOwnerConflict, get_local_owner
from .models import IncomeChange, IncomeEntry


class FinanceError(Exception):
    def __init__(self, message, status=400):
        self.message = message
        self.status = status


IncomeError = FinanceError  # Retain the existing income service interface.


def owner():
    try:
        user = get_local_owner()
    except LocalOwnerConflict:
        raise IncomeError("The local account could not be used.", 409)
    if user is None:
        raise IncomeError("Save your starting point before recording entries.", 409)
    return user


def month_bounds(month):
    if not re.fullmatch(r"[0-9]{4}-(0[1-9]|1[0-2])", month):
        raise IncomeError("Choose a month in YYYY-MM format.")
    year, number = map(int, month.split("-"))
    if year < 1:
        raise IncomeError("Choose a valid year.")
    return date(year, number, 1), date(year, number, calendar.monthrange(year, number)[1])


def list_income(month, page):
    user = owner()
    first, last = month_bounds(month)
    if not re.fullmatch(r"[1-9][0-9]{0,8}", page):
        raise IncomeError("Choose a valid page number.")
    entries = IncomeEntry.objects.filter(user=user, deleted_at__isnull=True, received_on__range=(first, last))
    total = entries.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    paginator = Paginator(entries, 25)
    try:
        selected = paginator.page(int(page))
    except EmptyPage:
        raise IncomeError("This page does not exist.")
    return selected, {"month": month, "total": format(total, ".2f"), "count": paginator.count, "page": selected.number, "pages": paginator.num_pages}


def get_income(entry_id, user, lock=False):
    entries = IncomeEntry.objects.filter(user=user, deleted_at__isnull=True)
    if lock:
        entries = entries.select_for_update()
    entry = entries.filter(pk=entry_id).first()
    if entry is None:
        raise IncomeError("This income entry could not be found.", 404)
    return entry


def snapshot(entry):
    return {
        "amount": format(entry.amount, ".2f"), "source": entry.source,
        "label": entry.label, "received_on": entry.received_on.isoformat(),
        "note": entry.note, "version": entry.version,
        "deleted": entry.deleted_at is not None,
    }


@transaction.atomic
def create_income(data):
    user = owner()
    User.objects.select_for_update().get(pk=user.pk)
    values = {key: value for key, value in data.items() if key != "request_key"}
    fingerprint = hashlib.sha256(json.dumps(values, sort_keys=True, default=str).encode()).hexdigest()
    existing = IncomeEntry.objects.filter(user=user, request_key=data["request_key"]).first()
    if existing:
        if existing.deleted_at or existing.creation_fingerprint != fingerprint:
            raise IncomeError("This submission was already used for a different or deleted entry. Reload before adding another.", 409)
        return existing, False
    entry = IncomeEntry(user=user, **values, request_key=data["request_key"], creation_fingerprint=fingerprint)
    entry.full_clean()
    entry.save()
    IncomeChange.objects.create(entry=entry, action="created", after=snapshot(entry))
    return entry, True


@transaction.atomic
def update_income(entry_id, data, delete=False):
    entry = get_income(entry_id, owner(), lock=True)
    if entry.version != data["expected_version"]:
        raise IncomeError("This entry changed since you opened it. Cancel and reload before trying again.", 409)
    before = snapshot(entry)
    if delete:
        entry.deleted_at = timezone.now()
    else:
        for key, value in data.items():
            if key != "expected_version":
                setattr(entry, key, value)
    entry.version += 1
    # Deleting a historical entry is allowed even if its date is now invalid.
    if not delete:
        entry.full_clean()
    entry.save()
    IncomeChange.objects.create(entry=entry, action="deleted" if delete else "updated", before=before, after=snapshot(entry))
    return entry

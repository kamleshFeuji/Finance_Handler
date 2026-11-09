import hashlib
import json
import re
from decimal import Decimal

from django.core.paginator import EmptyPage, Paginator
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.utils import timezone

from accounts.models import User
from .models import ExpenseCategory, ExpenseChange, ExpenseEntry, IncomeEntry
from .services import FinanceError, month_bounds, owner

DEFAULT_CATEGORIES = [
    ("Rent and housing", True), ("Food and groceries", True),
    ("Transportation", True), ("Utilities", True), ("Healthcare", True),
    ("Family responsibilities", True), ("Shopping", False),
    ("Entertainment", False), ("Travel", False), ("Education", True), ("Other expenses", False),
]


def ensure_default_categories(user):
    for name, essential in DEFAULT_CATEGORIES:
        ExpenseCategory.objects.get_or_create(user=user, normalized_name=name.casefold(), defaults={"name": name, "default_essential": essential})


def list_categories():
    return ExpenseCategory.objects.filter(user=owner())


@transaction.atomic
def save_category(data, category_id=None):
    user = owner()
    User.objects.select_for_update().get(pk=user.pk)
    category = None
    if category_id is not None:
        category = ExpenseCategory.objects.select_for_update().filter(user=user, pk=category_id).first()
        if category is None:
            raise FinanceError("Category not found.", 404)
        if category.version != data["expected_version"]:
            raise FinanceError("This category changed. Reload before trying again.", 409)
    normalized = data["name"].casefold()
    matches = ExpenseCategory.objects.filter(user=user, normalized_name=normalized)
    if category:
        matches = matches.exclude(pk=category.pk)
    if matches.exists():
        raise FinanceError("A category with this name already exists. You can restore it if archived.", 409)
    category = category or ExpenseCategory(user=user)
    category.name = data["name"]
    category.normalized_name = normalized
    category.default_essential = data["default_essential"]
    if category_id is not None:
        category.is_archived = data["is_archived"]
        category.version += 1
    category.full_clean()
    category.save()
    return category


def select_category(category_id, user, previous=None):
    category = ExpenseCategory.objects.select_for_update().filter(user=user, pk=category_id).first()
    if category is None or (category.is_archived and category_id != previous):
        raise FinanceError("Choose an active category from your list.")
    return category


def expense_totals(entries):
    sums = entries.aggregate(total=Sum("amount"), essential=Sum("amount", filter=Q(is_essential=True)))
    total = sums["total"] or Decimal("0.00")
    essential = sums["essential"] or Decimal("0.00")
    return {"total": format(total, ".2f"), "essential": format(essential, ".2f"), "optional": format(total - essential, ".2f")}


def category_totals(entries):
    grouped = entries.values("category_id", "category__name").annotate(total=Sum("amount"), count=Count("pk")).order_by("-total", "category__name")
    return [{"id": row["category_id"], "name": row["category__name"], "total": format(row["total"], ".2f"), "count": row["count"]} for row in grouped]


def list_expenses(month, page):
    user = owner()
    first, last = month_bounds(month)
    if not re.fullmatch(r"[1-9][0-9]{0,8}", page):
        raise FinanceError("Choose a valid page number.")
    entries = ExpenseEntry.objects.filter(user=user, deleted_at__isnull=True, spent_on__range=(first, last)).select_related("category")
    paginator = Paginator(entries, 25)
    try:
        selected = paginator.page(int(page))
    except EmptyPage:
        raise FinanceError("This page does not exist.")
    return selected, {"month": month, "page": selected.number, "pages": paginator.num_pages, "count": paginator.count, **expense_totals(entries), "categories": category_totals(entries)}


def get_expense(entry_id, user, lock=False):
    entries = ExpenseEntry.objects.filter(user=user, deleted_at__isnull=True)
    if lock:
        entries = entries.select_for_update()
    entry = entries.filter(pk=entry_id).first()
    if entry is None:
        raise FinanceError("This expense entry could not be found.", 404)
    return entry


def snapshot(entry):
    return {"amount": format(entry.amount, ".2f"), "category": entry.category_id, "category_name": entry.category.name, "is_essential": entry.is_essential, "spent_on": entry.spent_on.isoformat(), "label": entry.label, "note": entry.note, "version": entry.version, "deleted": entry.deleted_at is not None}


@transaction.atomic
def create_expense(data):
    user = owner()
    User.objects.select_for_update().get(pk=user.pk)
    values = {key: value for key, value in data.items() if key != "request_key"}
    fingerprint = hashlib.sha256(json.dumps(values, sort_keys=True, default=str).encode()).hexdigest()
    existing = ExpenseEntry.objects.filter(user=user, request_key=data["request_key"]).first()
    if existing:
        if existing.deleted_at or existing.creation_fingerprint != fingerprint:
            raise FinanceError("This submission was already used for a different or deleted expense. Reload before adding another.", 409)
        return existing, False
    category = select_category(values.pop("category"), user)
    entry = ExpenseEntry(user=user, category=category, **values, request_key=data["request_key"], creation_fingerprint=fingerprint)
    entry.full_clean()
    entry.save()
    ExpenseChange.objects.create(entry=entry, action="created", after=snapshot(entry))
    return entry, True


@transaction.atomic
def update_expense(entry_id, data, delete=False):
    user = owner()
    entry = get_expense(entry_id, user, lock=True)
    if entry.version != data["expected_version"]:
        raise FinanceError("This expense changed since you opened it. Cancel and reload before trying again.", 409)
    before = snapshot(entry)
    if delete:
        entry.deleted_at = timezone.now()
    else:
        entry.category = select_category(data["category"], user, previous=entry.category_id)
        for key, value in data.items():
            if key not in {"category", "expected_version"}:
                setattr(entry, key, value)
        entry.full_clean()
    entry.version += 1
    entry.save()
    ExpenseChange.objects.create(entry=entry, action="deleted" if delete else "updated", before=before, after=snapshot(entry))
    return entry


def overview(month):
    user = owner()
    first, last = month_bounds(month)
    income = IncomeEntry.objects.filter(user=user, deleted_at__isnull=True, received_on__range=(first, last))
    expenses = ExpenseEntry.objects.filter(user=user, deleted_at__isnull=True, spent_on__range=(first, last))
    recorded = income.aggregate(total=Sum("amount"), count=Count("pk"))
    total_income = recorded["total"] or Decimal("0.00")
    totals = expense_totals(expenses)
    return {"month": month, "income": format(total_income, ".2f"), "income_count": recorded["count"], "expenses": totals["total"], "expense_count": expenses.count(), "essential": totals["essential"], "optional": totals["optional"], "remaining": format(total_income - Decimal(totals["total"]), ".2f"), "categories": category_totals(expenses)}

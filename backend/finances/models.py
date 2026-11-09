import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class IncomeEntry(models.Model):
    class Source(models.TextChoices):
        SALARY = "salary", "Salary"
        FREELANCE = "freelance", "Freelance"
        ALLOWANCE = "allowance", "Allowance"
        OTHER = "other", "Other"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    source = models.CharField(max_length=20, choices=Source)
    label = models.CharField(max_length=100, blank=True)
    received_on = models.DateField()
    note = models.CharField(max_length=500, blank=True)
    request_key = models.UUIDField(default=uuid.uuid4)
    creation_fingerprint = models.CharField(max_length=64)
    version = models.PositiveIntegerField(default=1)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-received_on", "-id"]
        indexes = [models.Index(fields=["user", "received_on"], name="income_user_date_idx")]
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gt=0), name="income_amount_positive"),
            models.CheckConstraint(condition=models.Q(version__gte=1), name="income_version_positive"),
            models.UniqueConstraint(fields=["user", "request_key"], name="income_user_request_unique"),
        ]

    def clean(self):
        super().clean()
        if self.received_on and self.received_on > timezone.localdate():
            raise ValidationError({"received_on": "Record income only after you receive it."})


class IncomeChange(models.Model):
    """Private immutable audit snapshots; ownership derives from the entry."""
    entry = models.ForeignKey(IncomeEntry, on_delete=models.PROTECT, related_name="changes")
    action = models.CharField(max_length=10, choices=[("created", "Created"), ("updated", "Updated"), ("deleted", "Deleted")])
    before = models.JSONField(default=dict)
    after = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)


class ExpenseCategory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    normalized_name = models.CharField(max_length=100)
    default_essential = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    version = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["name", "id"]
        constraints = [models.UniqueConstraint(fields=["user", "normalized_name"], name="expense_category_user_name_unique")]


class ExpenseEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    is_essential = models.BooleanField()
    label = models.CharField(max_length=100, blank=True)
    spent_on = models.DateField()
    note = models.CharField(max_length=500, blank=True)
    request_key = models.UUIDField(default=uuid.uuid4)
    creation_fingerprint = models.CharField(max_length=64)
    version = models.PositiveIntegerField(default=1)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-spent_on", "-id"]
        indexes = [models.Index(fields=["user", "spent_on"], name="expense_user_date_idx")]
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gt=0), name="expense_amount_positive"),
            models.CheckConstraint(condition=models.Q(version__gte=1), name="expense_version_positive"),
            models.UniqueConstraint(fields=["user", "request_key"], name="expense_user_request_unique"),
        ]

    def clean(self):
        super().clean()
        if self.spent_on and self.spent_on > timezone.localdate():
            raise ValidationError({"spent_on": "Record an expense only after spending the money."})
        if self.category_id and self.user_id and self.category.user_id != self.user_id:
            raise ValidationError({"category": "Choose one of your own categories."})


class ExpenseChange(models.Model):
    entry = models.ForeignKey(ExpenseEntry, on_delete=models.PROTECT, related_name="changes")
    action = models.CharField(max_length=10, choices=[("created", "Created"), ("updated", "Updated"), ("deleted", "Deleted")])
    before = models.JSONField(default=dict)
    after = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

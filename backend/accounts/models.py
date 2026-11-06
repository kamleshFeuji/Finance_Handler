from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models


class User(AbstractUser):
    """Project user, defined before the first database migration."""


class UserFinancialProfile(models.Model):
    class IncomeType(models.TextChoices):
        SALARY = "salary", "Monthly salary"
        FREELANCE = "freelance", "Freelance or irregular income"
        ALLOWANCE = "allowance", "Allowance or part-time income"
        OTHER = "other", "Other income"

    class Priority(models.TextChoices):
        EMERGENCY = "emergency", "Build an emergency fund"
        SECURITY = "security", "Feel more financially secure"
        TRAVEL = "travel", "Save for travel and experiences"
        ENJOYMENT = "enjoyment", "Make room for hobbies and enjoyment"
        PURCHASE = "purchase", "Work toward a purchase or education"
        EXPLORE = "explore", "I'm still figuring it out"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    nickname = models.CharField(max_length=60, blank=True)
    income_type = models.CharField(max_length=20, choices=IncomeType, blank=True)
    expected_monthly_income = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    essential_monthly_expenses = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    existing_savings_estimate = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    priority = models.CharField(max_length=20, choices=Priority, blank=True)
    goal_ideas = models.CharField(max_length=500, blank=True)
    onboarding_completed_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(**{f"{field}__gte": 0}) | models.Q(**{f"{field}__isnull": True}),
                name=f"profile_{field}_nonnegative",
            )
            for field in ("expected_monthly_income", "essential_monthly_expenses", "existing_savings_estimate")
        ]

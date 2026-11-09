from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from .models import ExpenseCategory, ExpenseEntry
from .serializers import StrictInput


class CategoryInput(StrictInput):
    name = serializers.CharField(max_length=100)
    default_essential = serializers.BooleanField(default=False)

    def validate_name(self, value):
        name = " ".join(value.split())
        if len(name.casefold()) > 100:
            raise serializers.ValidationError("Use a shorter category name.")
        return name


class CategoryUpdate(CategoryInput):
    is_archived = serializers.BooleanField()
    expected_version = serializers.IntegerField(min_value=1)


class CategoryOutput(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = ["id", "name", "default_essential", "is_archived", "version"]


class ExpenseInput(StrictInput):
    amount = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=Decimal("0.01"))
    category = serializers.IntegerField(min_value=1)
    is_essential = serializers.BooleanField()
    spent_on = serializers.DateField()
    label = serializers.CharField(max_length=100, allow_blank=True, required=False, default="")
    note = serializers.CharField(max_length=500, allow_blank=True, required=False, default="")

    def validate_spent_on(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError("Record an expense only after spending the money.")
        return value


class ExpenseCreate(ExpenseInput):
    request_key = serializers.UUIDField()


class ExpenseUpdate(ExpenseInput):
    expected_version = serializers.IntegerField(min_value=1)


class ExpenseOutput(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name")

    class Meta:
        model = ExpenseEntry
        fields = ["id", "amount", "category", "category_name", "is_essential", "spent_on", "label", "note", "version", "created_at", "updated_at"]

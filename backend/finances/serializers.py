from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from .models import IncomeEntry


class StrictInput(serializers.Serializer):
    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError({"non_field_errors": ["Send a JSON object."]})
        unknown = set(data) - set(self.fields)
        if unknown:
            raise serializers.ValidationError({key: ["This field cannot be set."] for key in sorted(unknown)})
        return super().to_internal_value(data)


class IncomeInput(StrictInput):
    amount = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=Decimal("0.01"))
    source = serializers.ChoiceField(choices=IncomeEntry.Source.choices)
    label = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    received_on = serializers.DateField()
    note = serializers.CharField(max_length=500, required=False, allow_blank=True, default="")

    def validate_received_on(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError("Record income only after you receive it.")
        return value


class IncomeCreate(IncomeInput):
    request_key = serializers.UUIDField()


class IncomeUpdate(IncomeInput):
    expected_version = serializers.IntegerField(min_value=1)


class IncomeDelete(StrictInput):
    expected_version = serializers.IntegerField(min_value=1)


class IncomeOutput(serializers.ModelSerializer):
    class Meta:
        model = IncomeEntry
        fields = ["id", "amount", "source", "label", "received_on", "note", "version", "created_at", "updated_at"]

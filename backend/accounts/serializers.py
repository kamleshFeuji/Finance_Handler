from rest_framework import serializers

from .models import UserFinancialProfile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFinancialProfile
        fields = [
            "nickname", "income_type", "expected_monthly_income",
            "essential_monthly_expenses", "existing_savings_estimate",
            "priority", "goal_ideas", "onboarding_completed_at",
        ]
        read_only_fields = ["onboarding_completed_at"]
        extra_kwargs = {
            field: {"min_value": 0, "required": False, "allow_null": True}
            for field in ("expected_monthly_income", "essential_monthly_expenses", "existing_savings_estimate")
        }

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError({"non_field_errors": ["Send a JSON object."]})
        unknown = set(data) - (set(self.fields) - {"onboarding_completed_at"})
        if unknown:
            raise serializers.ValidationError({key: ["This field cannot be set."] for key in sorted(unknown)})
        return super().to_internal_value(data)

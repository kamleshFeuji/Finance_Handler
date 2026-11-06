from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.utils import timezone

from .models import User, UserFinancialProfile

LOCAL_USERNAME = "_savequest_local"


class LocalOwnerConflict(Exception):
    pass


def load_profile():
    return UserFinancialProfile.objects.filter(user__username=LOCAL_USERNAME).first()


@transaction.atomic
def save_profile(data):
    # No client may choose the owner. This account cannot be used for password login.
    user, _ = User.objects.get_or_create(
        username=LOCAL_USERNAME, defaults={"password": make_password(None)}
    )
    user = User.objects.select_for_update().get(pk=user.pk)
    if user.has_usable_password() or user.is_staff or user.is_superuser:
        raise LocalOwnerConflict
    profile = UserFinancialProfile.objects.filter(user=user).first()
    if profile is None:
        profile = UserFinancialProfile(user=user, onboarding_completed_at=timezone.now())
    # PUT is full replacement. Empty optional fields remain unknown, not zero.
    for field in ("nickname", "income_type", "priority", "goal_ideas"):
        setattr(profile, field, data.get(field, ""))
    for field in ("expected_monthly_income", "essential_monthly_expenses", "existing_savings_estimate"):
        setattr(profile, field, data.get(field))
    profile.full_clean()
    profile.save()
    return profile

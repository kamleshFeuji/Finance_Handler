from django.urls import path

from .views import health
from accounts.views import csrf, profile
from finances.views import expense_categories, expense_category_detail, expense_detail, expense_list, income_list, income_detail, overview

urlpatterns = [
    path("api/v1/health/", health, name="health"),
    path("api/v1/csrf/", csrf, name="csrf"),
    path("api/v1/profile/", profile, name="profile"),
    path("api/v1/income/", income_list, name="income-list"),
    path("api/v1/income/<int:entry_id>/", income_detail, name="income-detail"),
    path("api/v1/expenses/", expense_list, name="expense-list"),
    path("api/v1/expenses/<int:entry_id>/", expense_detail, name="expense-detail"),
    path("api/v1/expense-categories/", expense_categories, name="expense-categories"),
    path("api/v1/expense-categories/<int:category_id>/", expense_category_detail, name="expense-category-detail"),
    path("api/v1/overview/", overview, name="overview"),
]

from django.urls import path

from .views import health
from accounts.views import csrf, profile

urlpatterns = [
    path("api/v1/health/", health, name="health"),
    path("api/v1/csrf/", csrf, name="csrf"),
    path("api/v1/profile/", profile, name="profile"),
]

"""Public readiness endpoint; no user data or credentials are returned."""
from django.conf import settings
from django.db import DatabaseError, connection
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET


@require_GET
@never_cache
def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except DatabaseError:
        return JsonResponse({
            "app_name": settings.APP_DISPLAY_NAME,
            "status": "unavailable",
            "database": "unavailable",
        }, status=503)
    return JsonResponse({
        "app_name": settings.APP_DISPLAY_NAME,
        "status": "ok",
        "database": "connected",
    })

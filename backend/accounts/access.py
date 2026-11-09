from functools import wraps

from django.conf import settings
from django.db import DatabaseError
from django.http import JsonResponse


def local_only(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        host = request.get_host().split(":")[0]
        if not settings.LOCAL_SINGLE_USER or host not in {"localhost", "127.0.0.1"} or request.META.get("REMOTE_ADDR") not in {"127.0.0.1", "::1"}:
            return JsonResponse({"message": "This feature is available only on this computer."}, status=403)
        try:
            return view(request, *args, **kwargs)
        except DatabaseError:
            return JsonResponse({"message": "Your data could not be accessed. Check the database connection and apply migrations."}, status=503)
    return wrapped

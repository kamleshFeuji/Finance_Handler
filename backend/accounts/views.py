import json
from functools import wraps

from django.conf import settings
from django.db import DatabaseError
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET, require_http_methods

from .serializers import ProfileSerializer
from .services import LocalOwnerConflict, load_profile, save_profile


def local_only(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        host = request.get_host().split(":")[0]
        if not settings.LOCAL_SINGLE_USER or host not in {"localhost", "127.0.0.1"} or request.META.get("REMOTE_ADDR") not in {"127.0.0.1", "::1"}:
            return JsonResponse({"message": "This feature is available only on this computer."}, status=403)
        try:
            return view(request, *args, **kwargs)
        except DatabaseError:
            return JsonResponse({"message": "The profile could not be accessed. Check the database connection and apply migrations."}, status=503)
    return wrapped


@never_cache
@local_only
@require_GET
def csrf(request):
    return JsonResponse({"csrf_token": get_token(request)})


@never_cache
@local_only
@csrf_protect
@require_http_methods(["GET", "PUT"])
def profile(request):
    if request.method == "GET":
        instance = load_profile()
        return JsonResponse({"profile": ProfileSerializer(instance).data if instance else None})
    if request.content_type != "application/json":
        return JsonResponse({"message": "Use JSON for this request."}, status=415)
    try:
        data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"message": "The form could not be read. Please try again."}, status=400)
    serializer = ProfileSerializer(data=data)
    if not serializer.is_valid():
        return JsonResponse({"errors": serializer.errors}, status=400)
    try:
        instance = save_profile(serializer.validated_data)
    except LocalOwnerConflict:
        return JsonResponse({"message": "The reserved local account conflicts with an existing account."}, status=409)
    return JsonResponse({"profile": ProfileSerializer(instance).data})

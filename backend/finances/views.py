import json
from functools import wraps

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from accounts.access import local_only
from . import services
from .serializers import IncomeCreate, IncomeDelete, IncomeOutput, IncomeUpdate
from . import expense_services
from .expense_serializers import CategoryInput, CategoryOutput, CategoryUpdate, ExpenseCreate, ExpenseOutput, ExpenseUpdate


def income_errors(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        try:
            return view(request, *args, **kwargs)
        except services.IncomeError as error:
            return JsonResponse({"message": error.message}, status=error.status)
        except ValidationError as error:
            return JsonResponse({"errors": error.message_dict if hasattr(error, "message_dict") else {"non_field_errors": error.messages}}, status=400)
    return wrapped


def parse(request, serializer_class):
    if request.content_type != "application/json":
        raise services.IncomeError("Use JSON for this request.", 415)
    try:
        data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        raise services.IncomeError("The entry could not be read. Please try again.")
    serializer = serializer_class(data=data)
    serializer.is_valid()  # Return field-level validation rather than DRF's HTML error page.
    return serializer


@never_cache
@local_only
@csrf_protect
@require_http_methods(["GET", "POST"])
@income_errors
def income_list(request):
    if request.method == "GET":
        entries, summary = services.list_income(request.GET.get("month", timezone.localdate().strftime("%Y-%m")), request.GET.get("page", "1"))
        return JsonResponse({"results": IncomeOutput(entries, many=True).data, **summary})
    serializer = parse(request, IncomeCreate)
    if serializer.errors:
        return JsonResponse({"errors": serializer.errors}, status=400)
    entry, created = services.create_income(serializer.validated_data)
    return JsonResponse({"entry": IncomeOutput(entry).data}, status=201 if created else 200)


@never_cache
@local_only
@csrf_protect
@require_http_methods(["GET", "PUT", "DELETE"])
@income_errors
def income_detail(request, entry_id):
    if request.method == "GET":
        entry = services.get_income(entry_id, services.owner())
        return JsonResponse({"entry": IncomeOutput(entry).data})
    serializer = parse(request, IncomeDelete if request.method == "DELETE" else IncomeUpdate)
    if serializer.errors:
        return JsonResponse({"errors": serializer.errors}, status=400)
    entry = services.update_income(entry_id, serializer.validated_data, delete=request.method == "DELETE")
    if request.method == "DELETE":
        return JsonResponse({"message": "Income entry deleted."})
    return JsonResponse({"entry": IncomeOutput(entry).data})


@never_cache
@local_only
@csrf_protect
@require_http_methods(["GET", "POST"])
@income_errors
def expense_categories(request):
    if request.method == "GET":
        return JsonResponse({"results": CategoryOutput(expense_services.list_categories(), many=True).data})
    serializer = parse(request, CategoryInput)
    if serializer.errors:
        return JsonResponse({"errors": serializer.errors}, status=400)
    category = expense_services.save_category(serializer.validated_data)
    return JsonResponse({"category": CategoryOutput(category).data}, status=201)


@never_cache
@local_only
@csrf_protect
@require_http_methods(["PUT"])
@income_errors
def expense_category_detail(request, category_id):
    serializer = parse(request, CategoryUpdate)
    if serializer.errors:
        return JsonResponse({"errors": serializer.errors}, status=400)
    category = expense_services.save_category(serializer.validated_data, category_id)
    return JsonResponse({"category": CategoryOutput(category).data})


@never_cache
@local_only
@csrf_protect
@require_http_methods(["GET", "POST"])
@income_errors
def expense_list(request):
    if request.method == "GET":
        entries, summary = expense_services.list_expenses(request.GET.get("month", timezone.localdate().strftime("%Y-%m")), request.GET.get("page", "1"))
        return JsonResponse({"results": ExpenseOutput(entries, many=True).data, **summary})
    serializer = parse(request, ExpenseCreate)
    if serializer.errors:
        return JsonResponse({"errors": serializer.errors}, status=400)
    entry, created = expense_services.create_expense(serializer.validated_data)
    return JsonResponse({"entry": ExpenseOutput(entry).data}, status=201 if created else 200)


@never_cache
@local_only
@csrf_protect
@require_http_methods(["GET", "PUT", "DELETE"])
@income_errors
def expense_detail(request, entry_id):
    if request.method == "GET":
        entry = expense_services.get_expense(entry_id, services.owner())
        return JsonResponse({"entry": ExpenseOutput(entry).data})
    serializer = parse(request, IncomeDelete if request.method == "DELETE" else ExpenseUpdate)
    if serializer.errors:
        return JsonResponse({"errors": serializer.errors}, status=400)
    entry = expense_services.update_expense(entry_id, serializer.validated_data, delete=request.method == "DELETE")
    if request.method == "DELETE":
        return JsonResponse({"message": "Expense entry deleted."})
    return JsonResponse({"entry": ExpenseOutput(entry).data})


@never_cache
@local_only
@require_http_methods(["GET"])
@income_errors
def overview(request):
    return JsonResponse(expense_services.overview(request.GET.get("month", timezone.localdate().strftime("%Y-%m"))))

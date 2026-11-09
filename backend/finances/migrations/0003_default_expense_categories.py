from django.db import migrations

DEFAULTS = [
    ("Rent and housing", True), ("Food and groceries", True),
    ("Transportation", True), ("Utilities", True), ("Healthcare", True),
    ("Family responsibilities", True), ("Shopping", False),
    ("Entertainment", False), ("Travel", False), ("Education", True), ("Other expenses", False),
]


def add_defaults(apps, schema_editor):
    Profile = apps.get_model("accounts", "UserFinancialProfile")
    Category = apps.get_model("finances", "ExpenseCategory")
    alias = schema_editor.connection.alias
    for user_id in Profile.objects.using(alias).values_list("user_id", flat=True).iterator():
        for name, essential in DEFAULTS:
            Category.objects.using(alias).get_or_create(user_id=user_id, normalized_name=name.casefold(), defaults={"name": name, "default_essential": essential})


class Migration(migrations.Migration):
    dependencies = [("finances", "0002_expenses"), ("accounts", "0002_userfinancialprofile")]
    operations = [migrations.RunPython(add_defaults, migrations.RunPython.noop)]

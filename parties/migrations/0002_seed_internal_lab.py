from django.core.management import call_command
from django.db import migrations


def seed_internal_lab(apps, schema_editor):
    call_command("loaddata", "internal_lab", app_label="parties")


class Migration(migrations.Migration):
    dependencies = [
        ("parties", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_internal_lab, migrations.RunPython.noop),
    ]

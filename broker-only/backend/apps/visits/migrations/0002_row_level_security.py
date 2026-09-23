from django.db import migrations

from common.rls import enable_rls


class Migration(migrations.Migration):
    dependencies = [("visits", "0001_initial")]

    operations = [
        enable_rls("visits_visitplan"),
        enable_rls("visits_visitstop"),
        enable_rls("visits_syncmutation"),
    ]

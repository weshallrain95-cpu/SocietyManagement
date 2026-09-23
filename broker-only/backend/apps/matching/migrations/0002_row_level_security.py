from django.db import migrations

from common.rls import enable_rls


class Migration(migrations.Migration):
    dependencies = [("matching", "0001_initial")]

    operations = [
        enable_rls("matching_matchrun"),
        enable_rls("matching_matchresult"),
    ]

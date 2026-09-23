from django.db import migrations

from common.rls import enable_rls


class Migration(migrations.Migration):
    dependencies = [("inventory", "0002_initial")]

    operations = [
        enable_rls("inventory_listing"),
        enable_rls("inventory_keycustody"),
        enable_rls("inventory_uploadbatch"),
        enable_rls("inventory_uploadrow"),
        enable_rls("inventory_savedcolumnmapping"),
    ]

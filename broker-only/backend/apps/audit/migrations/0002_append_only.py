from django.db import migrations

from common.rls import forbid_update_delete


class Migration(migrations.Migration):
    dependencies = [("audit", "0001_initial")]

    operations = [
        forbid_update_delete("audit_auditevent"),
    ]

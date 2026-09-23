from django.db import migrations

from common.rls import enable_rls


class Migration(migrations.Migration):
    dependencies = [("crm", "0003_initial")]

    operations = [
        enable_rls("crm_customer"),
        enable_rls("crm_requirement"),
        enable_rls("crm_customerinteraction"),
        enable_rls("crm_shortlist"),
        enable_rls("crm_shortlistitem"),
    ]

from django.db import migrations

from common.rls import enable_rls


class Migration(migrations.Migration):
    """Invitations and withdrawals are private to the broker firm they concern; owner-side code reads them under platform_context."""

    dependencies = [("owners", "0001_initial")]

    operations = [
        enable_rls("owners_ownerinvite"),
        enable_rls("owners_ownerwithdrawal"),
    ]

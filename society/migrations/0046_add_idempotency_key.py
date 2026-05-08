from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ("society", "0045_safe_bank_and_ledger_v1"),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction",
            name="idempotency_key",
            field=models.CharField(
                max_length=100,
                null=True,
                blank=True,
            ),
        ),
    ]
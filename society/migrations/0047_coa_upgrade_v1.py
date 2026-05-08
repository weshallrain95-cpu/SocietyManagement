from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ("society", "0046_add_idempotency_key"),
    ]

    operations = [

        # 🔥 1. account_category
        migrations.AddField(
            model_name="chartofaccount",
            name="account_category",
            field=models.CharField(
                max_length=20,
                choices=[
                    ("BANK", "Bank"),
                    ("CASH", "Cash"),
                    ("MEMBER", "Member"),
                    ("VENDOR", "Vendor"),
                    ("FUND", "Fund"),
                    ("INCOME", "Income"),
                    ("EXPENSE", "Expense"),
                    ("GENERAL", "General"),
                ],
                default="GENERAL",
            ),
        ),

        # 🔥 2. subtype
        migrations.AddField(
            model_name="chartofaccount",
            name="subtype",
            field=models.CharField(
                max_length=30,
                choices=[
                    ("MAINTENANCE", "Maintenance"),
                    ("PARKING", "Parking"),
                    ("PENALTY", "Penalty"),
                    ("INTEREST", "Interest"),
                    ("TRANSFER", "Transfer Fee"),
                    ("AMENITY", "Amenity Income"),
                    ("RENTAL", "Rental Income"),
                    ("SERVICE", "Service Income"),
                    ("MISC", "Miscellaneous"),
                ],
                null=True,
                blank=True,
            ),
        ),

        # 🔥 3. is_postable
        migrations.AddField(
            model_name="chartofaccount",
            name="is_postable",
            field=models.BooleanField(
                default=True,
                help_text="Can transactions be posted directly to this account?",
            ),
        ),

        # 🔥 4. requires_entity
        migrations.AddField(
            model_name="chartofaccount",
            name="requires_entity",
            field=models.BooleanField(
                default=False,
                help_text="Requires member/vendor linkage for transactions",
            ),
        ),
    ]
